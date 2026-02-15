---
title: "Python Project Structure for Data Pipelines"
slug: python-project-structure-data
date: 2026-02-18
description: "How to organize a Python data pipeline project. Directory structure, configuration, testing, packaging. Build maintainable codebases."
categories: ["python"]
tags: ["python", "project-structure", "best-practices"]
draft: false
---

## Why Structure Matters

Start with one Python script. Works fine.

Add more features. The script grows to 500 lines. Then 1000. Then you can't find anything. Changing one thing breaks three others. New team members don't know where to look.

Poor structure = unmaintainable code = wasted time.

Good structure = self-documenting = easy to maintain.

## The Problem: Single Script Pipelines

```
pipeline.py  # 1200 lines of everything
```

Everything in one file:
- Database connections
- Extraction logic
- Transformation functions
- Loading functions
- Configuration
- Utility functions

This doesn't scale.

## Solution: Organized Project Structure

```
data-pipeline/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
├── config/
│   ├── __init__.py
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
└── scripts/
    ├── run_daily_pipeline.py
    └── backfill_date_range.py
```

Clear separation. Each file has one purpose.

## config/settings.py: Configuration

```python
"""
Pipeline configuration.
Load from environment variables.
"""

import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class PipelineConfig:
    source_db: DatabaseConfig
    target_db: DatabaseConfig
    batch_size: int
    max_retries: int


def load_config() -> PipelineConfig:
    """Load configuration from environment variables."""
    
    source_db = DatabaseConfig(
        host=os.getenv('SOURCE_DB_HOST', 'localhost'),
        port=int(os.getenv('SOURCE_DB_PORT', '5432')),
        database=os.getenv('SOURCE_DB_NAME', 'production'),
        user=os.getenv('SOURCE_DB_USER', 'user'),
        password=os.getenv('SOURCE_DB_PASSWORD', '')
    )
    
    target_db = DatabaseConfig(
        host=os.getenv('TARGET_DB_HOST', 'localhost'),
        port=int(os.getenv('TARGET_DB_PORT', '5432')),
        database=os.getenv('TARGET_DB_NAME', 'warehouse'),
        user=os.getenv('TARGET_DB_USER', 'user'),
        password=os.getenv('TARGET_DB_PASSWORD', '')
    )
    
    return PipelineConfig(
        source_db=source_db,
        target_db=target_db,
        batch_size=int(os.getenv('BATCH_SIZE', '10000')),
        max_retries=int(os.getenv('MAX_RETRIES', '3'))
    )
```

Configuration separate from logic. Easy to change. No hardcoded values.

## src/extract.py: Extraction Logic

```python
"""
Data extraction from source systems.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
import logging

logger = logging.getLogger(__name__)


def extract_orders(connection_string: str, process_date: date) -> pd.DataFrame:
    """
    Extract orders for a specific date.
    
    Args:
        connection_string: Database connection string
        process_date: Date to extract
        
    Returns:
        DataFrame with orders
    """
    logger.info(f"Extracting orders for {process_date}")
    
    engine = create_engine(connection_string)
    
    query = text("""
        SELECT
            order_id,
            customer_id,
            product_id,
            amount,
            order_date,
            status
        FROM orders
        WHERE DATE(order_date) = :process_date
    """)
    
    df = pd.read_sql(query, engine, params={'process_date': process_date})
    
    logger.info(f"Extracted {len(df)} orders")
    
    return df
```

## src/transform.py: Transformation Logic

```python
"""
Data transformations.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean orders data.
    
    - Remove duplicates
    - Drop nulls in critical fields
    - Standardize status values
    """
    logger.info(f"Cleaning {len(df)} orders")
    
    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates(subset=['order_id'])
    duplicates_removed = original_count - len(df)
    if duplicates_removed > 0:
        logger.warning(f"Removed {duplicates_removed} duplicate orders")
    
    # Drop nulls
    df = df.dropna(subset=['order_id', 'customer_id', 'amount'])
    
    # Standardize status
    status_map = {
        'complete': 'completed',
        'done': 'completed',
        'cancelled': 'canceled'
    }
    df['status'] = df['status'].str.lower().replace(status_map)
    
    logger.info(f"Cleaned data: {len(df)} orders remaining")
    
    return df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived metrics.
    """
    df = df.copy()
    
    # Flag high-value orders
    df['is_high_value'] = df['amount'] > 1000
    
    # Extract date parts
    df['order_month'] = pd.to_datetime(df['order_date']).dt.to_period('M')
    df['order_year'] = pd.to_datetime(df['order_date']).dt.year
    
    return df
```

## src/load.py: Loading Logic

```python
"""
Data loading to target systems.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
import logging

logger = logging.getLogger(__name__)


def load_orders(df: pd.DataFrame, connection_string: str, process_date: date):
    """
    Load orders to warehouse (idempotent).
    
    Args:
        df: DataFrame to load
        connection_string: Target database connection
        process_date: Date partition to load
    """
    logger.info(f"Loading {len(df)} orders for {process_date}")
    
    engine = create_engine(connection_string)
    
    with engine.begin() as conn:
        # Delete existing data for this date (idempotent)
        conn.execute(
            text("DELETE FROM warehouse.orders WHERE DATE(order_date) = :date"),
            {'date': process_date}
        )
        logger.info(f"Deleted existing orders for {process_date}")
    
    # Insert new data
    df.to_sql(
        'orders',
        engine,
        schema='warehouse',
        if_exists='append',
        index=False
    )
    
    logger.info(f"Successfully loaded {len(df)} orders")
```

## scripts/run_daily_pipeline.py: Orchestration

```python
"""
Run daily orders pipeline.
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_orders
from src.transform import clean_orders, calculate_metrics
from src.load import load_orders
from config.settings import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline(process_date: datetime.date):
    """
    Run the full pipeline for a specific date.
    """
    logger.info(f"Starting pipeline for {process_date}")
    
    # Load config
    config = load_config()
    
    try:
        # Extract
        df = extract_orders(
            config.source_db.connection_string,
            process_date
        )
        
        # Transform
        df = clean_orders(df)
        df = calculate_metrics(df)
        
        # Load
        load_orders(
            df,
            config.target_db.connection_string,
            process_date
        )
        
        logger.info(f"Pipeline completed successfully for {process_date}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == '__main__':
    # Default: yesterday
    process_date = datetime.now().date() - timedelta(days=1)
    
    # Or from command line: python run_daily_pipeline.py 2025-01-15
    if len(sys.argv) > 1:
        process_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    
    run_pipeline(process_date)
```

## scripts/backfill_date_range.py: Backfilling

```python
"""
Backfill pipeline for a date range.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_daily_pipeline import run_pipeline


def backfill(start_date: datetime.date, end_date: datetime.date):
    """Backfill pipeline for date range."""
    
    current_date = start_date
    
    while current_date <= end_date:
        print(f"Processing {current_date}")
        
        try:
            run_pipeline(current_date)
        except Exception as e:
            print(f"Failed for {current_date}: {e}")
            # Continue with next date
        
        current_date += timedelta(days=1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python backfill_date_range.py START_DATE END_DATE")
        print("Example: python backfill_date_range.py 2025-01-01 2025-01-31")
        sys.exit(1)
    
    start = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    end = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
    
    backfill(start, end)
```

## requirements.txt

```
pandas==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pytest==7.4.3
```

## .env.example

```
# Source database
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=production
SOURCE_DB_USER=user
SOURCE_DB_PASSWORD=password

# Target database
TARGET_DB_HOST=localhost
TARGET_DB_PORT=5432
TARGET_DB_NAME=warehouse
TARGET_DB_USER=user
TARGET_DB_PASSWORD=password

# Pipeline settings
BATCH_SIZE=10000
MAX_RETRIES=3
```

## README.md

```markdown
# Orders Data Pipeline

Daily pipeline to extract, transform, and load orders data.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

## Usage

```bash
# Run for yesterday
python scripts/run_daily_pipeline.py

# Run for specific date
python scripts/run_daily_pipeline.py 2025-01-15

# Backfill date range
python scripts/backfill_date_range.py 2025-01-01 2025-01-31
```

## Testing

```bash
pytest tests/
```
```

## Why This Structure Works

**Separation of concerns**: Extract, transform, load are independent.

**Testable**: Each module can be tested separately.

**Reusable**: transform.py can be used by multiple pipelines.

**Clear entry points**: scripts/ folder shows how to run things.

**Configuration separate**: Change databases without touching code.

**Scalable**: Add new pipelines without mess.

## What to Avoid

**Don't:** Mix configuration and logic.
**Don't:** Put everything in `utils.py` (vague name = dumping ground).
**Don't:** Create deep nested folders (flat is better).
**Don't:** Name files `helper.py` or `common.py` (be specific).

## Summary

Structure your Python pipelines:
- config/ for settings
- src/ for pipeline logic
- tests/ for tests
- scripts/ for entry points

Organized code = maintainable code = productive team.
