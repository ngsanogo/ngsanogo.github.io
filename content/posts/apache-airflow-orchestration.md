---
authors:
  - Issa Sanogo
categories:
  - Application
  - Infrastructure
date: "2025-12-03"
lastmod: "2025-12-03"
description: "Apache Airflow explained: How data engineers schedule and monitor data pipelines at scale."
tags:
  - airflow
  - orchestration
  - data-pipeline
  - scheduling
title: "Apache Airflow: Orchestrate Your Data Pipelines"
draft: false
weight: 6
toc: true
---

## What is Apache Airflow?

Airflow schedules and monitors your data pipelines.

You tell it: "Run this pipeline daily at 2 AM. If it fails, retry 3 times. Alert me if it still fails."

Airflow does that. Automatically. Reliably.

## The Problem It Solves

You have multiple data pipelines:

- Extract from Salesforce (daily at 2 AM)
- Extract from Google Analytics (daily at 3 AM)
- Transform and combine (daily at 4 AM)
- Load to warehouse (daily at 5 AM)
- Send alerts to stakeholders (daily at 6 AM)

Without Airflow: You manually run each script. Or use cron jobs (primitive, hard to manage).

With Airflow: Define the workflow once. It handles scheduling, retries, notifications, everything.

## How Airflow Works

**DAG (Directed Acyclic Graph)**: A workflow. Tasks and their dependencies.

```
Extract Salesforce → Transform → Load
Extract Analytics  ↗
```

Airflow understands this graph. Runs tasks in the right order. Waits for dependencies.

**Tasks**: Individual units of work. Run a Python script, execute SQL, call an API.

**Scheduler**: Runs in the background. Checks which tasks should run. Executes them.

**Web UI**: Dashboard showing all pipelines, status, logs, history.

## Real Example: E-Commerce Daily Report

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_sales_report',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2025, 1, 1),
)

def extract_orders():
    # Connect to database, extract orders
    print("Extracting orders...")

def transform_data():
    # Clean, aggregate, calculate totals
    print("Transforming data...")

def load_warehouse():
    # Load into data warehouse
    print("Loading to warehouse...")

def send_alert():
    # Email report to stakeholders
    print("Sending alert...")

# Define tasks
extract = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_orders,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag,
)

load = PythonOperator(
    task_id='load',
    python_callable=load_warehouse,
    dag=dag,
)

alert = PythonOperator(
    task_id='send_alert',
    python_callable=send_alert,
    dag=dag,
)

# Define dependencies
extract >> transform >> load >> alert
```

That's it. Airflow runs the entire workflow every day at 2 AM.

## Why Data Engineers Need Airflow

**Reliability**: Automatic retries. If task fails, Airflow retries 3 times before giving up.

**Monitoring**: Web dashboard shows every pipeline. Status, duration, logs.

**Alerting**: Failures trigger email alerts. You know immediately something broke.

**Scalability**: Run 100 pipelines simultaneously. Airflow manages resources.

**Visibility**: Historical data. See what ran, when it ran, how long it took.

**Dependency management**: If task A fails, task B doesn't run. Smart.

## Key Airflow Concepts

**Operator**: Task that does work.

```python
BashOperator(task_id='run_script', bash_command='python script.py')
PythonOperator(task_id='my_task', python_callable=my_function)
```

**Sensor**: Waits for something to happen.

```python
FileSensor(task_id='wait_for_file', filepath='/data/input.csv')
```

**XCom (Cross Communication)**: Tasks share data.

```python
# Task 1 pushes data
ti.xcom_push(key='count', value=1000)

# Task 2 pulls data
count = ti.xcom_pull(task_ids='task1', key='count')
```

**Hooks**: Connection to external systems.

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

hook = PostgresHook(postgres_conn_id='my_postgres')
result = hook.get_records('SELECT * FROM customers')
```

## Real-World Airflow Usage

**Morning workflow**:

- 2 AM: Extract from databases
- 3 AM: Extract from APIs
- 4 AM: Transform and clean
- 5 AM: Load to warehouse
- 6 AM: Generate reports
- 7 AM: Send to stakeholders

All automated. No manual work.

**Monitoring**:

- Task took 30 minutes instead of 5 minutes? Alert.
- Task failed? Retry. Fail again? Email sent.
- Historical view: "This task has failed 3 times this month. Investigate."

## Common Airflow Patterns

**Parallel execution**:

```python
# Task 1 and Task 2 run simultaneously
extract_salesforce >> load
extract_analytics >> load
```

**Conditional execution**:

```python
from airflow.operators.python import BranchPythonOperator

def choose_path():
    if some_condition:
        return 'task_a'
    else:
        return 'task_b'

branch = BranchPythonOperator(
    task_id='branching',
    python_callable=choose_path,
)
```

**Dynamic tasks**:

```python
# Generate tasks based on list of tables
tables = ['customers', 'orders', 'products']

for table in tables:
    task = PythonOperator(
        task_id=f'extract_{table}',
        python_callable=extract_data,
        op_kwargs={'table': table},
    )
```

## Airflow vs Cron vs Manual

**Manual**:

- You run scripts yourself
- Easy to forget
- No monitoring
- No alerts

**Cron**:

- Automatic scheduling
- No retry logic
- No monitoring
- Limited visibility
- Hard to coordinate dependencies

**Airflow**:

- Automatic scheduling
- Built-in retry logic
- Full monitoring and alerting
- Complete visibility
- Handles complex dependencies
- Web UI for management

Clear winner: Airflow.

## Getting Started with Airflow

```bash
# Install
pip install apache-airflow

# Initialize database
airflow db init

# Create user
airflow users create --role Admin --username admin --email admin@example.com --firstname John --lastname Doe --password admin

# Start scheduler (in background)
airflow scheduler &

# Start web server
airflow webserver --port 8080

# Visit http://localhost:8080
```

Create a DAG file in the `dags/` folder. Airflow detects it automatically.

## Airflow Best Practices

**Keep tasks small**: One job per task.

**Use clear naming**: `extract_customers`, not `task1`.

**Set timeouts**: Prevent tasks from running forever.

```python
PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    execution_timeout=timedelta(minutes=30),
)
```

**Monitor SLA (Service Level Agreement)**:

```python
dag = DAG(
    'my_dag',
    sla=timedelta(hours=1),  # Task must complete in 1 hour
)
```

**Use environment variables for secrets**:

```python
import os
db_password = os.getenv('DB_PASSWORD')
```

## Real Example: Monitoring in Airflow

You can see:

- When each task ran
- How long it took
- If it succeeded or failed
- Full logs of what happened
- Previous runs of the same task
- Trends over time

This visibility is invaluable. You know your pipelines are working. You know when they're not. You fix problems fast.

## Airflow Ecosystem

**Providers**: Connectors to external systems.

- Google Cloud (BigQuery, Cloud Storage)
- AWS (S3, Redshift)
- Databricks
- Snowflake
- PostgreSQL
- MySQL
- And hundreds more

Install what you need:

```bash
pip install apache-airflow-providers-google
pip install apache-airflow-providers-amazon
```

## Bottom Line

Airflow is how serious data engineering happens.

Without Airflow: Manual scheduling, no monitoring, fragile.

With Airflow: Automatic, monitored, reliable, scalable.

Every data team uses Airflow (or similar). It's not optional for serious data work.

Learn Airflow. Use it daily. Your pipelines will be more reliable and easier to manage.
