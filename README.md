
#  Inventory Tracker & Supply Chain System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Java](https://img.shields.io/badge/Java-Spring%20Boot-orange.svg)
![Python](https://img.shields.io/badge/Python-Flask-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)

A hybrid Java + Python inventory management system with a Spring Boot backend for core business logic, a Flask-based AI prediction microservice, and a PostgreSQL database. Tracks inventory items, sales history, and provides data-driven stock-out predictions.

---

##  Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Database Setup](#database-setup)
  - [Running the Java Backend](#running-the-java-backend)
  - [Running the Python Predictor Service](#running-the-python-predictor-service)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Security Notes](#security-notes)
- [Contributing](#contributing)

---

##  Features

-  **Inventory tracking** — Manage items, stock levels, and product details via `InventoryItem`
-  **Sales history** — Record and query historical sales data through `SalesHistory`
-  **AI stock-out prediction** — Flask microservice (`predictor.py`) calculates which item is closest to running out based on average daily sales over the last 30 days
-  **REST API** — Clean endpoints served by Spring Boot with a static frontend (`index.html`)
-  **Python analytics layer** — Decoupled prediction service using `psycopg2` + `statistics` for data analysis
-  **CORS-enabled** — Frontend and backend can run on separate ports during development

---

## 🛠 Tech Stack

| Layer               | Technology                        |
|---------------------|-----------------------------------|
| Core Backend        | Java, Spring Boot (Maven)         |
| Prediction Service  | Python 3, Flask, Flask-CORS       |
| Database            | PostgreSQL                        |
| DB Driver (Python)  | psycopg2                          |
| Build Tool          | Maven Wrapper (`mvnw`)            |
| Frontend            | Static HTML (`index.html`)        |
| Data Generation     | Python (`generate_data.py`)       |
| Testing             | JUnit (`InventoryApplicationTests`) |

---

## 🗂 Project Structure

```
inventory/
├── src/
│   └── main/
│       ├── java/com/project/inventory/
│       │   ├── InventoryApplication.java       # Spring Boot entry point
│       │   ├── InventoryController.java        # REST controllers
│       │   ├── InventoryItem.java              # Entity: inventory item
│       │   ├── InventoryRepository.java        # JPA repository for inventory
│       │   ├── SalesHistory.java               # Entity: sales record
│       │   ├── SalesHistoryRepository.java     # JPA repository for sales
│       │   └── SalesHistorySummary.java        # DTO/summary projection
│       └── resources/
│           ├── static/
│           │   └── index.html                  # Frontend UI
│           └── application.properties          # Spring Boot config
├── test/
│   └── java/com/project/inventory/
│       └── InventoryApplicationTests.java      # Integration tests
├── predictor.py                                # Flask AI prediction microservice
├── generate_data.py                            # Script to seed sample data
├── pom.xml                                     # Maven dependencies
├── mvnw / mvnw.cmd                             # Maven wrapper scripts
├── .gitignore
└── .gitattributes
```

---

##  Getting Started

### Prerequisites

- **Java** 17+
- **Maven** (or use the included `mvnw` wrapper)
- **Python** 3.8+
- **PostgreSQL** 14+

---

### Database Setup

1. Create the database:

```bash
psql -U postgres -c "CREATE DATABASE inventory_db;"
```

2. Spring Boot will auto-create tables via JPA on first run.

3. Optionally seed sample data:

```bash
python generate_data.py
```

---

### Running the Java Backend

```bash
# Using Maven wrapper (recommended)
./mvnw spring-boot:run

# On Windows
mvnw.cmd spring-boot:run
```

The Spring Boot app will start at `http://localhost:8080`.

---

### Running the Python Predictor Service

1. Install Python dependencies:

```bash
pip install flask flask-cors psycopg2-binary
```

2. Set your database password as an environment variable (see [Security Notes](#security-notes)):

```bash
export DB_PASSWORD=your_password_here
```

3. Start the Flask service:

```bash
python predictor.py
```

The predictor API will be available at `http://localhost:5000`.

---

## 📡 API Reference

### Java Backend — port `8080`

| Method | Endpoint              | Description                  |
|--------|-----------------------|------------------------------|
| GET    | `/api/inventory`      | List all inventory items     |
| POST   | `/api/inventory`      | Add a new inventory item     |
| PUT    | `/api/inventory/{id}` | Update an existing item      |
| DELETE | `/api/inventory/{id}` | Remove an item               |
| GET    | `/api/sales`          | Get sales history            |
| POST   | `/api/sales`          | Record a new sale            |

### Python Predictor Service — port `5000`

| Method | Endpoint       | Description                                                                |
|--------|----------------|----------------------------------------------------------------------------|
| GET    | `/api/predict` | Returns the item closest to running out based on avg daily sales (30 days) |

**Example response:**
```json
{
  "item_name": "Widget A",
  "current_stock": 12,
  "avg_daily_sales": 3.4,
  "days_remaining": 3
}
```

---

##  Configuration

### Spring Boot — `application.properties`

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/inventory_db
spring.datasource.username=postgres
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

### Python Predictor — Environment Variables

```bash
export DB_HOST=localhost
export DB_NAME=inventory_db
export DB_USER=postgres
export DB_PASSWORD=your_secure_password
```

---

##  Security Notes

>  **Never hardcode database credentials in source code.**

Update `predictor.py` to read credentials from environment variables:

```python
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'inventory_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD')
    )
```

- Add `.env` to your `.gitignore` if using a `.env` file
- If a password was ever pushed to a public repository, **rotate it immediately**

---

## Running Tests

```bash
./mvnw test
```

---

##  Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add: your feature"`
4. Push and open a Pull Request

---
