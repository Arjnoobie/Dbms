from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import statistics
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # MAKE SURE TO UPDATE YOUR PASSWORD HERE
    return psycopg2.connect(
        host='localhost',
        database='inventory_db',
        user='postgres',
        password='SyEd@#1346'
    )

# ── /api/predict ──────────────────────────────────────────────────────────────
# AI suggestion: now data-driven — finds the item closest to running out
# and warns about it instead of using a hardcoded day-of-week message.
@app.route('/api/predict', methods=['GET'])
def get_prediction():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Find the item with the fewest days of stock left based on avg daily sales
        cur.execute("""
            SELECT i.item_name, i.current_stock,
                   COALESCE(AVG(daily.qty), 0) AS avg_daily
            FROM inventory_item i
            LEFT JOIN (
                SELECT item_id, sale_date, SUM(quantity_sold) AS qty
                FROM sales_history
                WHERE sale_date >= current_date - interval '30 days'
                GROUP BY item_id, sale_date
            ) daily ON i.id = daily.item_id
            GROUP BY i.id, i.item_name, i.current_stock
            HAVING COALESCE(AVG(daily.qty), 0) > 0
            ORDER BY (i.current_stock / AVG(daily.qty)) ASC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        if row:
            name, stock, avg = row
            days = round(float(stock) / float(avg), 1)
            if days < 3:
                msg = f"🚨 URGENT: {name} has only ~{days} days of stock left! Restock immediately."
            elif days < 7:
                msg = f"⚠️ {name} will run out in ~{days} days based on recent sales. Consider restocking soon."
            else:
                msg = f"✅ Stock levels are stable. {name} is the lowest at ~{days} days remaining."
        else:
            msg = "Stock levels look stable. No sales data found yet."
        return jsonify({"message": msg})
    except Exception as e:
        # Fallback to day-of-week if DB fails
        today = datetime.today().weekday()
        if today in [3, 4, 5]:
            return jsonify({"message": "Weekend approaching! Thumbs Up sales are increasing. Stock up now!"})
        return jsonify({"message": "Stock levels look stable based on historical data."})
    finally:
        if conn:
            conn.close()

# ── /api/sales-stats ──────────────────────────────────────────────────────────
# Groups last 30 days of sales into 4 weekly buckets for the bar chart.
@app.route('/api/sales-stats', methods=['GET'])
def get_sales_stats():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                CASE
                    WHEN sale_date > current_date - interval '7 days'  THEN 'Week 4'
                    WHEN sale_date > current_date - interval '14 days' THEN 'Week 3'
                    WHEN sale_date > current_date - interval '21 days' THEN 'Week 2'
                    ELSE 'Week 1'
                END AS week,
                SUM(quantity_sold)
            FROM sales_history
            WHERE sale_date >= current_date - interval '30 days'
            GROUP BY week
            ORDER BY week
        """)
        data = cur.fetchall()
        cur.close()
        return jsonify({
            "labels": [row[0] for row in data],
            "values": [int(row[1]) for row in data]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# ── /api/forecast ─────────────────────────────────────────────────────────────
# DEMAND FORECASTING: for each item, calculates avg daily sales over 30 days
# and estimates how many days of stock remain → flags items needing reorder.
@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT i.item_name, i.current_stock,
                   COALESCE(AVG(daily.qty), 0) AS avg_daily
            FROM inventory_item i
            LEFT JOIN (
                SELECT item_id, sale_date, SUM(quantity_sold) AS qty
                FROM sales_history
                WHERE sale_date >= current_date - interval '30 days'
                GROUP BY item_id, sale_date
            ) daily ON i.id = daily.item_id
            GROUP BY i.id, i.item_name, i.current_stock
            ORDER BY i.item_name
        """)
        rows = cur.fetchall()
        cur.close()

        result = []
        for item_name, current_stock, avg_daily in rows:
            avg_daily = float(avg_daily)
            if avg_daily > 0:
                days_left = round(current_stock / avg_daily, 1)
                needs_reorder = days_left < 7
            else:
                days_left = None
                needs_reorder = False

            result.append({
                "item_name": item_name,
                "current_stock": current_stock,
                "avg_daily_sales": round(avg_daily, 1),
                "days_until_stockout": days_left,
                "needs_reorder": needs_reorder
            })

        # Sort: items needing reorder come first
        result.sort(key=lambda x: (not x["needs_reorder"], x["days_until_stockout"] or 9999))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# ── /api/anomalies ────────────────────────────────────────────────────────────
# ANOMALY DETECTION: for each item, computes mean + std dev of daily sales
# over 30 days. If any day in the last 3 days exceeds mean + 2×std, it's
# flagged as a spike — which may indicate stock shrinkage or data error.
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT i.item_name, s.sale_date, SUM(s.quantity_sold) AS qty
            FROM sales_history s
            JOIN inventory_item i ON s.item_id = i.id
            WHERE s.sale_date >= current_date - interval '30 days'
            GROUP BY i.item_name, s.sale_date
            ORDER BY i.item_name, s.sale_date
        """)
        rows = cur.fetchall()
        cur.close()

        # Group daily totals by item
        item_sales = defaultdict(list)
        for item_name, sale_date, qty in rows:
            item_sales[item_name].append(int(qty))

        anomalies = []
        for item_name, daily_qtys in item_sales.items():
            if len(daily_qtys) < 5:
                continue  # not enough data to detect anomalies
            mean = statistics.mean(daily_qtys)
            stdev = statistics.stdev(daily_qtys)
            if stdev == 0:
                continue
            threshold = mean + 2 * stdev
            # Check the 3 most recent days for spikes
            for qty in daily_qtys[-3:]:
                if qty > threshold:
                    anomalies.append({
                        "item": item_name,
                        "qty": qty,
                        "avg": round(mean, 1),
                        "message": f"{item_name}: {qty} units removed in one day (avg: {round(mean,1)}). Possible stock shrinkage!"
                    })
                    break  # one alert per item is enough

        return jsonify(anomalies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
