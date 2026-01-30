---
title: "Apache Airflow: Orchestrate Your Data Pipelines"
slug: apache-airflow-orchestration
date: 2024-12-03
description: "Apache Airflow explained: How data engineers schedule and monitor data pipelines at scale."
draft: false
---
## What is Apache Airflow?

Airflow schedules and monitors your data pipelines.

You tell it: "Run this pipeline daily at 2 AM. If it fails, retry 3 times. Alert me if it still fails."

Airflow handles everything else.

## The Problem It Solves

Manual execution fails. You forget to run things. You run them twice. You can't see what's happening.

Airflow automates and visualizes your entire workflow.

## Key Concepts

**DAG (Directed Acyclic Graph)**: Your workflow definition. It's code that describes what runs when.

**Task**: A single step in your DAG. Could be: run SQL query, call API, move files, send email.

**Operator**: The type of task. BashOperator runs bash commands. PythonOperator runs Python functions. PostgresOperator runs SQL.

**Schedule**: When your DAG runs. Daily. Hourly. Every Monday at 9 AM. Whatever you need.

## Simple DAG Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extracting data...")

def transform():
    print("Transforming data...")

def load():
    print("Loading data...")

with DAG(
    dag_id="simple_etl",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:
    
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract
    )
    
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform
    )
    
    load_task = PythonOperator(
        task_id="load",
        python_callable=load
    )
    
    extract_task >> transform_task >> load_task
```

This DAG runs daily. Extract first. Then transform. Then load.

## The Airflow UI

Airflow provides a web interface. You can:

- See all your DAGs
- Check run history
- View logs for each task
- Manually trigger runs
- See task dependencies visually

This visibility is valuable. You know exactly what ran, when, and if it succeeded.

## When to Use Airflow

**Good for:**
- Scheduled batch pipelines
- Multi-step workflows
- Complex dependencies
- When you need monitoring and alerting

**Not ideal for:**
- Real-time streaming (use Kafka instead)
- Simple one-off scripts
- Very small projects

## Installation

```bash
pip install apache-airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start webserver
airflow webserver --port 8080

# Start scheduler (in another terminal)
airflow scheduler
```

## Common Patterns

**Branching**: Run different tasks based on conditions.

**Sensors**: Wait for something to happen (file arrives, API responds).

**XCom**: Pass data between tasks.

**Pools**: Limit concurrent task execution.

**Variables**: Store configuration values.

## Real-World DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["alerts@company.com"]
}

with DAG(
    dag_id="sales_report",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="0 6 * * *",  # Every day at 6 AM
    catchup=False
) as dag:
    
    extract_sales = PostgresOperator(
        task_id="extract_sales",
        postgres_conn_id="sales_db",
        sql="SELECT * FROM sales WHERE date = '{{ ds }}'"
    )
    
    calculate_metrics = PythonOperator(
        task_id="calculate_metrics",
        python_callable=calculate_daily_metrics
    )
    
    send_report = EmailOperator(
        task_id="send_report",
        to="manager@company.com",
        subject="Daily Sales Report {{ ds }}",
        html_content="See attached report."
    )
    
    extract_sales >> calculate_metrics >> send_report
```

This DAG extracts sales data, calculates metrics, sends email report. Daily at 6 AM. Retries on failure. Alerts on persistent failure.

## Best Practices

**Keep DAGs simple**: One DAG, one purpose. Don't build mega-DAGs.

**Idempotent tasks**: Running twice should produce the same result.

**Use connections**: Don't hardcode credentials in DAGs.

**Test locally**: Validate DAG syntax before deploying.

**Monitor**: Check the Airflow UI regularly. Set up alerts.

## Summary

Airflow orchestrates data pipelines. You define workflows as code. Airflow schedules, executes, and monitors them.

It's complex to set up. But for production data pipelines, it's essential.

Start simple. One DAG. Few tasks. Expand as needed.
