"""
CSV Load Script for Urban Mobility Data Explorer
Demonstrates loading and inspecting the raw train.csv dataset
"""

import pandas as pd
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('csv_load.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_csv(file_path='train.csv'):
    """
    Load and inspect the raw CSV dataset
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        pandas DataFrame with loaded data
    """
    try:
        logger.info("=" * 60)
        logger.info("CSV Load Script Started")
        logger.info("=" * 60)
        logger.info("Target file: %s", file_path)
        
        # Load CSV
        logger.info("Loading CSV file...")
        start_time = datetime.now()
        
        df = pd.read_csv(file_path, low_memory=False)
        
        end_time = datetime.now()
        load_duration = (end_time - start_time).total_seconds()
        
        logger.info("CSV loaded successfully in %.2f seconds", load_duration)
        logger.info("=" * 60)
        
        # Dataset Information
        logger.info("DATASET OVERVIEW")
        logger.info("=" * 60)
        logger.info("Total rows: %d", len(df))
        logger.info("Total columns: %d", len(df.columns))
        logger.info("Memory usage: %.2f MB", df.memory_usage(deep=True).sum() / (1024 * 1024))
        
        # Column Information
        logger.info("=" * 60)
        logger.info("COLUMN DETAILS")
        logger.info("=" * 60)
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            non_null = df[col].count()
            null_count = df[col].isna().sum()
            logger.info("%d. %s - Type: %s, Non-null: %d, Null: %d", 
                       i, col, dtype, non_null, null_count)
        
        # Sample Data
        logger.info("=" * 60)
        logger.info("FIRST 5 ROWS")
        logger.info("=" * 60)
        logger.info("\n%s", df.head().to_string())
        
        # Data Statistics
        logger.info("=" * 60)
        logger.info("NUMERIC COLUMN STATISTICS")
        logger.info("=" * 60)
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            logger.info("\n%s", df[numeric_cols].describe().to_string())
        else:
            logger.info("No numeric columns found")
        
        # Data Quality Check
        logger.info("=" * 60)
        logger.info("DATA QUALITY CHECK")
        logger.info("=" * 60)
        total_cells = df.shape[0] * df.shape[1]
        total_missing = df.isna().sum().sum()
        missing_percentage = (total_missing / total_cells) * 100
        
        logger.info("Total cells: %d", total_cells)
        logger.info("Missing values: %d (%.2f%%)", total_missing, missing_percentage)
        logger.info("Complete rows: %d", df.dropna().shape[0])
        logger.info("Duplicate rows: %d", df.duplicated().sum())
        
        # Summary
        logger.info("=" * 60)
        logger.info("LOAD SUMMARY")
        logger.info("=" * 60)
        logger.info("✓ CSV file successfully loaded")
        logger.info("✓ %d rows and %d columns processed", len(df), len(df.columns))
        logger.info("✓ Log file saved to: csv_load.log")
        logger.info("=" * 60)
        
        return df
        
    except FileNotFoundError:
        logger.error("CSV file not found: %s", file_path)
        logger.error("Please ensure the file exists in the current directory")
        raise
    except Exception as e:
        logger.error("Error loading CSV: %s", e)
        raise


def main():
    """Main entry point"""
    try:
        df = load_csv('train.csv')
        logger.info("CSV load completed successfully!")
        logger.info("DataFrame shape: %s", df.shape)
        
    except Exception as e:
        logger.error("CSV load failed: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
