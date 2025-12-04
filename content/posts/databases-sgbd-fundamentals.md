---
authors:
  - Issa Sanogo
categories:
  - Application
date: "2025-11-26"
lastmod: "2025-11-26"
description: "Understanding databases (SGBD): What they are, how they work, and why every data engineer needs to know them."
tags:
  - database
  - sgbd
  - data-storage
  - fundamentals
title: "Databases (SGBD): The Foundation of Data Storage"
draft: false
weight: 8
toc: true
---

## What is a Database?

A database (SGBD - Système de Gestion de Base de Données in French) is organized data storage.

Think of it as a sophisticated filing system that lets you find, modify, and organize millions of records instantly.

Without databases, companies couldn't operate. No way to store customer data, orders, inventory, nothing.

## The Problem It Solves

Imagine a company without a database:

**File storage**:

- Customer data in 1000 CSV files
- Search for a customer? Open 1000 files. Find them manually.
- Update their info? Edit the file. Hope you don't mess up.
- Ensure consistency? Good luck.

**Database**:

- All customer data in one place
- Search for a customer? Instant
- Update their info? One command
- Consistency guaranteed
- Millions of records? No problem

Databases make companies functional.

## Types of Databases

**Relational (SQL)**: Data in tables with relationships.

```
Customers table:
  id | name | email | signup_date

Orders table:
  id | customer_id | amount | date
```

Most common. Used everywhere. PostgreSQL, MySQL, SQL Server.

**No-SQL (Document)**: Data in flexible documents.

```json
{
  "id": 1,
  "name": "John",
  "email": "john@example.com",
  "orders": [...]
}
```

More flexible. Less structured. MongoDB, Cassandra.

**Time-series**: Data indexed by time.

```
timestamp | metric | value
2025-12-04 10:00 | cpu_usage | 45%
2025-12-04 10:01 | cpu_usage | 52%
```

For metrics, logs, sensors. InfluxDB, Prometheus.

**Graph**: Data with relationships.

```
Person -> knows -> Person
Person -> created -> Post
```

For networks, recommendations. Neo4j.

**Data Warehouses**: Optimized for analysis.

Snowflake, BigQuery, Redshift. Massive datasets. Complex queries. Fast analysis.

For data engineers: Master relational databases first. SQL is essential. Others come later.

## How Relational Databases Work

**Tables**: Collections of related data.

```
Customers:
┌────┬──────────┬──────────────────┬─────────────┐
│ id │ name     │ email            │ signup_date │
├────┼──────────┼──────────────────┼─────────────┤
│ 1  │ Alice    │ alice@example.com│ 2025-01-15  │
│ 2  │ Bob      │ bob@example.com  │ 2025-02-20  │
│ 3  │ Carol    │ carol@example.com│ 2025-03-10  │
└────┴──────────┴──────────────────┴─────────────┘
```

**Primary Key**: Unique identifier for each row.

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,  -- Unique
    name TEXT
);
```

**Foreign Key**: Link to another table.

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),  -- Links to customers
    amount DECIMAL
);
```

**Index**: Fast lookup.

```sql
CREATE INDEX idx_email ON customers(email);
-- Now searching by email is fast
```

## Real Example: E-Commerce Database

**Tables**:

```
Customers: id, name, email, address
Orders: id, customer_id, order_date, total
OrderItems: id, order_id, product_id, quantity, price
Products: id, name, category, stock
```

**Relationships**:

```
Customer has many Orders
Order has many OrderItems
OrderItem references Product
```

**Queries**:

```sql
-- Find all orders for a customer
SELECT * FROM orders WHERE customer_id = 1;

-- Find what products Alice ordered
SELECT p.name, oi.quantity
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE c.name = 'Alice';

-- Find customers who spent more than $1000
SELECT c.name, SUM(o.total)
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
HAVING SUM(o.total) > 1000;
```

## Key Database Concepts

**ACID**: Guarantees data safety.

- **Atomicity**: Transaction completes or doesn't. No partial updates.
- **Consistency**: Data is always valid.
- **Isolation**: Concurrent transactions don't interfere.
- **Durability**: Once saved, data stays saved.

**Transaction**: Multiple operations as one unit.

```sql
BEGIN;
  UPDATE customers SET balance = balance - 100 WHERE id = 1;
  UPDATE customers SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- Both updates succeed or both fail. No partial transfer.
```

**Normalization**: Organize data to avoid duplicates.

```
Bad: Store customer name in every order row (repeated data)
Good: Store customer_id in orders, name in customers (no duplication)
```

**Denormalization**: Sometimes duplicate for speed.

```
Data warehouse: Store customer name in orders table for faster queries
(slower to update, faster to query)
```

## What Data Engineers Do With Databases

**Extract**: Pull data for processing.

```sql
SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '1 day';
```

**Validate**: Check data quality.

```sql
SELECT COUNT(*) FROM customers WHERE email IS NULL;
```

**Transform**: Modify and aggregate.

```sql
SELECT
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(amount) as total
FROM orders
GROUP BY month;
```

**Load**: Move cleaned data to warehouse.

```sql
INSERT INTO warehouse.customer_summary
SELECT customer_id, COUNT(*), SUM(amount)
FROM orders
GROUP BY customer_id;
```

**Monitor**: Track health.

```sql
SELECT COUNT(*) as row_count FROM orders;
SELECT MAX(updated_at) as last_update FROM customers;
```

## Database Performance

**Slow query**:

```sql
SELECT * FROM orders WHERE order_date LIKE '%2025%';
-- Slow: Full table scan
```

**Fast query**:

```sql
CREATE INDEX idx_order_date ON orders(order_date);
SELECT * FROM orders WHERE order_date >= '2025-01-01';
-- Fast: Uses index
```

**Slow join**:

```sql
SELECT * FROM orders, customers WHERE orders.customer_id = customers.id;
-- Slow: No index on foreign key
```

**Fast join**:

```sql
-- Foreign key creates index automatically
SELECT * FROM orders
JOIN customers ON orders.customer_id = customers.id;
-- Fast: Uses foreign key index
```

## Common Database Issues

**Connection timeout**: Too many connections.

```sql
-- Check connections
SELECT COUNT(*) FROM pg_stat_activity;
```

**Full table scan**: No index, slow query.

```sql
-- Add index
CREATE INDEX idx_status ON orders(status);
```

**Data inconsistency**: Data out of sync.

```sql
-- Use transactions to prevent this
BEGIN;
  -- Multiple operations
COMMIT;
```

**Backup needed**: Disaster recovery.

```bash
pg_dump mydb > backup.sql
```

## SQL vs No-SQL Databases

**SQL (Relational)**:

- ✓ Structured data
- ✓ Complex queries
- ✓ ACID guarantees
- ✗ Less flexible schema
- ✗ Slower for unstructured data

**No-SQL (Document)**:

- ✓ Flexible schema
- ✓ Fast for unstructured data
- ✓ Horizontal scaling
- ✗ Less structured
- ✗ Complex queries harder

For data engineering: Start with SQL. It's more predictable and reliable.

## Getting Started With Databases

**Install PostgreSQL**:

```bash
# Download from postgresql.org
# Or use Docker
docker run -e POSTGRES_PASSWORD=password postgres:15
```

**Connect**:

```bash
psql -U postgres
```

**Create table**:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Insert data**:

```sql
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
```

**Query**:

```sql
SELECT * FROM users;
```

**Update**:

```sql
UPDATE users SET name = 'Alice Smith' WHERE id = 1;
```

**Delete**:

```sql
DELETE FROM users WHERE id = 1;
```

## Real Database Scenario

You're building a pipeline that processes customer orders daily.

**Step 1: Connect to production database**

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@prod-db:5432/orders')
```

**Step 2: Extract new orders**

```python
df = pd.read_sql(
    'SELECT * FROM orders WHERE created_at > NOW() - INTERVAL 1 DAY',
    engine
)
```

**Step 3: Clean and transform**

```python
df = df.drop_duplicates()
df['total'] = df['qty'] * df['price']
```

**Step 4: Load to warehouse**

```python
warehouse = create_engine('postgresql://user:pass@warehouse:5432/data')
df.to_sql('daily_orders', warehouse, if_exists='append')
```

Done. Happens daily. Data flows from production to warehouse.

## Bottom Line

Databases are foundational to data engineering.

You must understand:

- How data is organized
- How to query it
- How to load and transform it
- Performance considerations
- ACID guarantees

Master SQL and relational databases. Everything else builds on that foundation.
