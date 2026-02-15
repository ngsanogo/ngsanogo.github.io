---
title: "SQL Query Optimization: Make Queries Fast"
slug: sql-query-optimization
date: 2026-02-17
description: "How to optimize slow SQL queries. Understand indexes, execution plans, and common performance patterns. Make your queries 10x faster."
categories: ["sql"]
tags: ["sql", "performance", "optimization", "postgresql"]
draft: false
---

## Why Queries Are Slow

Your query returns correct results but takes 10 minutes. Users complain. Dashboards timeout. Pipelines miss SLAs.

Slow queries have predictable causes:
- No indexes
- Wrong indexes
- Full table scans
- Inefficient joins
- Bad query structure

Fix these, queries get fast.

## Finding Slow Queries

PostgreSQL tracks query performance:

```sql
-- Enable query stats (run once)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

This shows what's actually slow in production.

## Understanding EXPLAIN

`EXPLAIN` shows how PostgreSQL executes your query:

```sql
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE customer_id = 123;
```

Output:

```
Seq Scan on orders  (cost=0.00..1000.00 rows=50 width=100) (actual time=0.05..150.23 rows=47 loops=1)
  Filter: (customer_id = 123)
  Rows Removed by Filter: 999953
Planning Time: 0.134 ms
Execution Time: 150.421 ms
```

**Seq Scan** = full table scan = slow.

**Rows Removed by Filter: 999953** = checked 1 million rows, kept 47 = very inefficient.

## Fix 1: Add an Index

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

Run `EXPLAIN ANALYZE` again:

```
Index Scan using idx_orders_customer_id on orders  (cost=0.42..8.44 rows=50 width=100) (actual time=0.03..0.15 rows=47 loops=1)
  Index Cond: (customer_id = 123)
Planning Time: 0.085 ms
Execution Time: 0.189 ms
```

**Index Scan** = used index = fast.
**Execution Time: 0.189 ms** (was 150ms) = 800x faster.

## Common Slow Query Patterns

### Pattern 1: Missing Index on Foreign Key

```sql
-- Slow: No index on customer_id
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.country = 'France';
```

Fix:

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_customers_country ON customers(country);
```

### Pattern 2: Function on Indexed Column

```sql
-- Slow: Function prevents index usage
SELECT * FROM orders WHERE DATE(created_at) = '2025-01-01';
```

This full scans `orders` even if `created_at` is indexed.

Fix:

```sql
-- Fast: Range comparison uses index
SELECT * FROM orders
WHERE created_at >= '2025-01-01'
  AND created_at < '2025-01-02';
```

### Pattern 3: OR Conditions

```sql
-- Slow: OR prevents efficient index usage
SELECT * FROM orders WHERE customer_id = 123 OR status = 'pending';
```

Fix (if both WHERE clauses are selective):

```sql
-- Fast: UNION uses indexes on both
SELECT * FROM orders WHERE customer_id = 123
UNION
SELECT * FROM orders WHERE status = 'pending';
```

### Pattern 4: SELECT *

```sql
-- Slow: Fetches unnecessary columns
SELECT * FROM orders WHERE customer_id = 123;
```

Fix:

```sql
-- Fast: Only fetch needed columns
SELECT id, amount, created_at FROM orders WHERE customer_id = 123;
```

Smaller result sets = less memory = faster.

### Pattern 5: Implicit Type Conversion

```sql
-- Slow: customer_id is INTEGER but '123' is string
SELECT * FROM orders WHERE customer_id = '123';
```

PostgreSQL converts customer_id to text for each row = index not used.

Fix:

```sql
-- Fast: Correct type
SELECT * FROM orders WHERE customer_id = 123;
```

## Composite Indexes

When you filter on multiple columns:

```sql
-- Query filters on customer_id AND created_at
SELECT * FROM orders
WHERE customer_id = 123
  AND created_at >= '2025-01-01';
```

Single column indexes help, but composite index is better:

```sql
CREATE INDEX idx_orders_customer_created ON orders(customer_id, created_at);
```

Order matters: `(customer_id, created_at)` works for:
- `WHERE customer_id = X`
- `WHERE customer_id = X AND created_at > Y`

But not for:
- `WHERE created_at > Y` (doesn't use index)

## Indexes Have a Cost

**Benefits:**
- Fast SELECT queries
- Fast JOIN operations

**Costs:**
- INSERT/UPDATE/DELETE slower (index must update)
- Disk space
- Maintenance overhead

Don't index everything. Index what your queries actually use.

## Analyzing a Slow Query: Real Example

```sql
-- This query takes 30 seconds
SELECT
    c.name,
    COUNT(o.id) as order_count,
    SUM(o.amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.country = 'France'
  AND o.created_at >= '2025-01-01'
GROUP BY c.id, c.name;
```

Run `EXPLAIN ANALYZE`:

```
Hash Join  (cost=50000.00..100000.00 rows=10000 width=50) (actual time=5000.23..29542.18 rows=8437 loops=1)
  Hash Cond: (o.customer_id = c.id)
  -> Seq Scan on orders o  (cost=0.00..45000.00 rows=500000 width=20) (actual time=0.05..15234.12 rows=500000 loops=1)
       Filter: (created_at >= '2025-01-01'::date)
       Rows Removed by Filter: 1500000
  -> Hash  (cost=35000.00..35000.00 rows=5000 width=30) (actual time=250.45..250.45 rows=4972 loops=1)
       -> Seq Scan on customers c  (cost=0.00..35000.00 rows=5000 width=30) (actual time=0.12..245.67 rows=4972 loops=1)
             Filter: (country = 'France'::text)
             Rows Removed by Filter: 95028
```

**Problems:**
1. Seq Scan on orders (checked 2M rows, kept 500k)
2. Seq Scan on customers (checked 100k rows, kept 5k)

**Fix:**

```sql
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_orders_customer_created ON orders(customer_id, created_at);
```

Run again:

```
Hash Join  (cost=250.00..1500.00 rows=10000 width=50) (actual time=12.34..145.67 rows=8437 loops=1)
  Hash Cond: (o.customer_id = c.id)
  -> Index Scan using idx_orders_customer_created on orders o  (cost=0.56..1200.00 rows=500000 width=20) (actual time=0.03..98.45 rows=500000 loops=1)
       Index Cond: (created_at >= '2025-01-01'::date)
  -> Hash  (cost=200.00..200.00 rows=5000 width=30) (actual time=2.45..2.45 rows=4972 loops=1)
       -> Index Scan using idx_customers_country on customers c  (cost=0.42..200.00 rows=5000 width=30) (actual time=0.02..1.89 rows=4972 loops=1)
             Index Cond: (country = 'France'::text)
```

**Result: 29s → 0.15s** (200x faster).

## When to Analyze

```sql
-- After bulk inserts/updates, update statistics
ANALYZE orders;
```

PostgreSQL's query planner uses statistics to choose execution plans. Outdated statistics = bad plans = slow queries.

## Partitioning Large Tables

For tables with time-series data:

```sql
-- Partition by month
CREATE TABLE orders (
    id SERIAL,
    customer_id INTEGER,
    amount DECIMAL,
    created_at DATE
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2025_01 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE orders_2025_02 PARTITION OF orders
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

Queries filtering on `created_at` only scan relevant partitions.

## Summary

Slow queries have predictable fixes:
1. Find slow queries (`pg_stat_statements`)
2. Understand execution plan (`EXPLAIN ANALYZE`)
3. Add indexes where full scans happen
4. Rewrite queries to use indexes
5. Update statistics (`ANALYZE`)

Most queries can be 10-100x faster with correct indexes.
