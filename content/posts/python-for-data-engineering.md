---
authors:
  - Issa Sanogo
categories:
  - Application
date: "2025-11-27"
lastmod: "2025-11-27"
description: "Python for data engineering: Why it's essential, what you use it for, and how to get started."
tags:
  - python
  - programming
  - data-engineering
  - scripting
title: "Python: The Language Data Engineers Use Daily"
draft: false
weight: 7
toc: true
---

## What is Python?

Python is a programming language. Easy to read. Powerful. Flexible.

Data engineers use it for everything: extract data, transform data, build pipelines, automate tasks, analyze data.

## Why Python for Data Engineering?

**Readable**: Code looks like English.

```python
customers = get_data_from_database('customers')
cleaned = remove_duplicates(customers)
save_to_warehouse(cleaned)
```

Compare to other languages: Much more complicated.

**Libraries**: Thousands of libraries for data work.

- Pandas: Manipulate data
- NumPy: Math and arrays
- SQLAlchemy: Talk to databases
- Requests: Get data from APIs
- PySpark: Big data processing

**Community**: Huge Python community. Answers to every question exist.

**Industry standard**: Every data company uses Python. Period.

## What You Do With Python in Data Engineering

**Extract data**:

```python
import requests
response = requests.get('https://api.example.com/customers')
data = response.json()
```

**Transform data**:

```python
import pandas as pd

df = pd.read_csv('orders.csv')
df['total'] = df['quantity'] * df['price']
df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
```

**Load data**:

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/mydb')
df.to_sql('orders_processed', engine, if_exists='append')
```

**Automate tasks**:

```python
import schedule
import time

def run_pipeline():
    extract()
    transform()
    load()

schedule.every().day.at("2:00").do(run_pipeline)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Build pipelines**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

# Define workflow
extract >> transform >> load
```

## Core Python Libraries for Data Engineers

**Pandas**: Manipulate data like spreadsheets.

```python
import pandas as pd

df = pd.read_csv('data.csv')
df['total'] = df['qty'] * df['price']
df.groupby('category').sum()
```

**SQLAlchemy**: Talk to any database.

```python
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://user:pass@localhost/mydb')
result = engine.execute(text('SELECT * FROM customers'))
```

**Requests**: Get data from APIs.

```python
import requests

response = requests.get('https://api.github.com/users/github')
data = response.json()
```

**PySpark**: Process large data.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('myapp').getOrCreate()
df = spark.read.csv('large_file.csv')
df.filter(df.age > 25).show()
```

**Logging**: Track what your code does.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Starting pipeline')
logger.error('Pipeline failed')
```

## Real Example: Extract, Transform, Load in Python

```python
import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract():
    """Extract data from database"""
    logger.info('Extracting data...')
    engine = create_engine('postgresql://user:pass@localhost/mydb')
    df = pd.read_sql('SELECT * FROM raw_orders', engine)
    return df

def transform(df):
    """Clean and transform data"""
    logger.info('Transforming data...')

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove nulls
    df = df.dropna()

    # Calculate totals
    df['total'] = df['quantity'] * df['price']

    # Add month
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')

    return df

def load(df):
    """Load data to warehouse"""
    logger.info('Loading data...')
    engine = create_engine('postgresql://user:pass@localhost/warehouse')
    df.to_sql('orders_processed', engine, if_exists='append', index=False)
    logger.info(f'Loaded {len(df)} rows')

# Run pipeline
try:
    df = extract()
    df = transform(df)
    load(df)
    logger.info('Pipeline completed successfully')
except Exception as e:
    logger.error(f'Pipeline failed: {e}')
```

## Python Best Practices

**Use virtual environments**:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Keep requirements.txt**:

```
pandas==2.1.0
sqlalchemy==2.0.23
requests==2.31.0
python-dotenv==1.0.0
```

**Use logging, not print()**:

```python
# Bad
print("Data loaded")

# Good
logger.info("Data loaded")
```

**Handle errors**:

```python
try:
    connect_to_database()
except ConnectionError:
    logger.error("Database connection failed")
    raise
```

**Use functions**:

```python
# Bad
data = read_csv('file.csv')
data['total'] = data['qty'] * data['price']
data.to_csv('output.csv')

# Good
def process_orders(input_file, output_file):
    data = read_csv(input_file)
    data['total'] = data['qty'] * data['price']
    data.to_csv(output_file)

process_orders('input.csv', 'output.csv')
```

**Use environment variables for secrets**:

```python
import os

db_password = os.getenv('DB_PASSWORD')
api_key = os.getenv('API_KEY')
```

## Common Python Patterns in Data Engineering

**Reading from multiple sources**:

```python
df1 = pd.read_csv('file1.csv')
df2 = pd.read_sql('SELECT * FROM table2', engine)
df3 = requests.get('https://api.example.com/data').json()

combined = pd.concat([df1, df2, df3])
```

**Batch processing**:

```python
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    process_chunk(chunk)
```

**Error handling**:

```python
def get_data_safely(query):
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f'Query failed: {e}')
        return None
```

**Parallel processing**:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_item, items)
```

## Python vs Other Languages for Data Engineering

**Python**: Readable, lots of libraries, easy to learn. Best for most data work.

**Scala**: Faster for big data. More complex. Used with Spark.

**SQL**: Essential. But limited (transformation only). Always paired with Python.

**R**: Good for statistics. Less used in production. More academic.

**Java**: Complex. Only for specific systems. Not recommended.

For data engineering: Python is the right choice.

## Getting Started with Python

**Install Python 3.11**:

```bash
# Download from python.org
python --version
```

**Create project**:

```bash
mkdir my_project
cd my_project
python -m venv venv
source venv/bin/activate
```

**Install libraries**:

```bash
pip install pandas sqlalchemy requests
```

**Write simple script**:

```python
import pandas as pd

df = pd.read_csv('data.csv')
print(f"Loaded {len(df)} rows")
print(df.head())
```

**Run it**:

```bash
python script.py
```

That's it. You're doing Python data engineering.

## The Python Ecosystem

**Development**: Write code

- VS Code, PyCharm

**Testing**: Verify code works

- pytest, unittest

**Documentation**: Explain code

- docstrings, markdown

**Packaging**: Share code

- pip, setuptools

**CI/CD**: Automate deployment

- GitHub Actions, Jenkins

These tools make Python professional and reliable.

## Real Example: Daily Pipeline in Python

```python
#!/usr/bin/env python3
"""Daily ETL pipeline"""

import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main pipeline"""
    logger.info('Pipeline started')

    # Extract
    engine = create_engine('postgresql://user:pass@localhost/mydb')
    df = pd.read_sql(
        'SELECT * FROM orders WHERE created_at > NOW() - INTERVAL 1 DAY',
        engine
    )
    logger.info(f'Extracted {len(df)} rows')

    # Transform
    df['total'] = df['quantity'] * df['price']
    df['date'] = pd.to_datetime(df['created_at']).dt.date

    # Load
    warehouse = create_engine('postgresql://user:pass@localhost/warehouse')
    df.to_sql('daily_orders', warehouse, if_exists='append', index=False)
    logger.info(f'Loaded {len(df)} rows to warehouse')

    logger.info('Pipeline completed')

if __name__ == '__main__':
    main()
```

Schedule this to run daily with Airflow or cron. Done.

## Bottom Line

Python is the language data engineers use every day.

Master Python basics. Learn libraries (pandas, SQLAlchemy, requests). Write clean code.

You'll be valuable to any data team.
