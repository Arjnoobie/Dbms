import psycopg2
from datetime import datetime, timedelta
import random

def seed_sales():
    # Update the password to yours!
    conn = psycopg2.connect(host='localhost', database='inventory_db', user='postgres', password='SyEd@#1346')
    cur = conn.cursor()

    # 1. Get all your existing item IDs from inventory_item
    cur.execute("SELECT id FROM inventory_item")
    item_ids = [row[0] for row in cur.fetchall()]

    # 2. Clear old data if any exists
    cur.execute("DELETE FROM sales_history")

    # 3. Generate 30 days of data for EACH item
    for item_id in item_ids:
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            # Random sales per item per day
            qty = random.randint(2, 12)
            cur.execute(
                "INSERT INTO sales_history (item_id, sale_date, quantity_sold) VALUES (%s, %s, %s)",
                (item_id, date, qty)
            )

    conn.commit()
    print(f"Successfully generated 30 days of sales for {len(item_ids)} items!")
    cur.close()
    conn.close()

seed_sales()