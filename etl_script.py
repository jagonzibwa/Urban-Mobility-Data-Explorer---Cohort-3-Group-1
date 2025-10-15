"""
ETL Script for Urban Mobility Data Explorer
Extracts data from CSV, Transforms it, and Loads into SQLite database
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UrbanMobilityETL:
    """ETL pipeline for urban mobility trip data"""
    
    def __init__(self, db_path='database.db', csv_path='data.csv'):
        """
        Initialize ETL pipeline
        
        Args:
            db_path: Path to SQLite database
            csv_path: Path to source CSV file
        """
        self.db_path = db_path
        self.csv_path = csv_path
        self.conn = None
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_database(self):
        """Initialize database schema from database.sql"""
        try:
            with open('database.sql', 'r') as f:
                schema_sql = f.read()
            
            cursor = self.conn.cursor()
            cursor.executescript(schema_sql)
            self.conn.commit()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def extract_data(self, chunksize=10000):
        """
        Extract data from CSV file in chunks
        
        Args:
            chunksize: Number of rows to process at a time
            
        Yields:
            DataFrame chunks
        """
        try:
            logger.info(f"Starting data extraction from {self.csv_path}")
            
            # Read CSV in chunks to handle large files
            for chunk_num, chunk in enumerate(pd.read_csv(
                self.csv_path, 
                chunksize=chunksize,
                low_memory=False
            ), 1):
                logger.info(f"Extracted chunk {chunk_num} with {len(chunk)} rows")
                yield chunk
                
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise
    
    def transform_data(self, df):
        """
        Transform and clean the data
        
        Args:
            df: Raw DataFrame from CSV
            
        Returns:
            Dictionary containing transformed dataframes for each table
        """
        logger.info("Starting data transformation")
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Handle missing values
        df = df.dropna(subset=['pickup_datetime', 'dropoff_datetime'])
        
        # Convert datetime columns
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
        
        # Calculate trip duration in seconds if not present
        if 'trip_duration' not in df.columns:
            df['trip_duration'] = (
                df['dropoff_datetime'] - df['pickup_datetime']
            ).dt.total_seconds().astype(int)
        
        # Remove invalid trips (negative duration or too long)
        df = df[
            (df['trip_duration'] > 0) & 
            (df['trip_duration'] < 86400)  # Less than 24 hours
        ]
        
        # Extract and create Vendor data
        vendors = df[['vendor_id', 'vendor_name']].drop_duplicates() \
            if 'vendor_name' in df.columns else \
            pd.DataFrame({'vendor_id': df['vendor_id'].unique()})
        
        if 'vendor_name' not in vendors.columns:
            vendors['vendor_name'] = 'Vendor ' + vendors['vendor_id'].astype(str)
        
        # Extract and create Location data for pickup
        pickup_locations = df[['pickup_location_id', 'pickup_longitude', 'pickup_latitude']].copy()
        pickup_locations.columns = ['location_id', 'longitude', 'latitude']
        
        # Extract and create Location data for dropoff
        dropoff_locations = df[['dropoff_location_id', 'dropoff_longitude', 'dropoff_latitude']].copy()
        dropoff_locations.columns = ['location_id', 'longitude', 'latitude']
        
        # Combine and deduplicate locations
        locations = pd.concat([pickup_locations, dropoff_locations]) \
            .drop_duplicates(subset=['location_id']) \
            .dropna()
        
        # Prepare Trip data
        trip_columns = [
            'vendor_id', 'pickup_location_id', 'dropoff_location_id',
            'pickup_datetime', 'dropoff_datetime', 'passenger_count',
            'trip_duration'
        ]
        
        # Add optional column if exists
        if 'store_and_fwd_flag' in df.columns:
            trip_columns.append('store_and_fwd_flag')
        
        trips = df[trip_columns].copy()
        
        # Ensure passenger_count is valid
        trips['passenger_count'] = trips['passenger_count'].fillna(1).astype(int)
        trips = trips[trips['passenger_count'] > 0]
        
        logger.info(f"Transformation complete: {len(vendors)} vendors, "
                   f"{len(locations)} locations, {len(trips)} trips")
        
        return {
            'vendors': vendors,
            'locations': locations,
            'trips': trips
        }
    
    def load_data(self, transformed_data):
        """
        Load transformed data into database
        
        Args:
            transformed_data: Dictionary containing transformed dataframes
        """
        logger.info("Starting data loading")
        cursor = self.conn.cursor()
        
        try:
            # Load Vendors
            vendors = transformed_data['vendors']
            for _, vendor in vendors.iterrows():
                cursor.execute(
                    """INSERT OR IGNORE INTO Vendor (vendor_id, vendor_name) 
                       VALUES (?, ?)""",
                    (int(vendor['vendor_id']), vendor['vendor_name'])
                )
            logger.info(f"Loaded {len(vendors)} vendors")
            
            # Load Locations
            locations = transformed_data['locations']
            for _, location in locations.iterrows():
                cursor.execute(
                    """INSERT OR IGNORE INTO Location (location_id, longitude, latitude) 
                       VALUES (?, ?, ?)""",
                    (int(location['location_id']), 
                     float(location['longitude']), 
                     float(location['latitude']))
                )
            logger.info(f"Loaded {len(locations)} locations")
            
            # Load Trips
            trips = transformed_data['trips']
            for _, trip in trips.iterrows():
                try:
                    if 'store_and_fwd_flag' in trip:
                        cursor.execute(
                            """INSERT INTO Trip 
                               (vendor_id, pickup_location_id, dropoff_location_id,
                                pickup_datetime, dropoff_datetime, passenger_count,
                                store_and_fwd_flag, trip_duration)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (int(trip['vendor_id']),
                             int(trip['pickup_location_id']),
                             int(trip['dropoff_location_id']),
                             trip['pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             trip['dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             int(trip['passenger_count']),
                             trip['store_and_fwd_flag'],
                             int(trip['trip_duration']))
                        )
                    else:
                        cursor.execute(
                            """INSERT INTO Trip 
                               (vendor_id, pickup_location_id, dropoff_location_id,
                                pickup_datetime, dropoff_datetime, passenger_count,
                                trip_duration)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (int(trip['vendor_id']),
                             int(trip['pickup_location_id']),
                             int(trip['dropoff_location_id']),
                             trip['pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             trip['dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             int(trip['passenger_count']),
                             int(trip['trip_duration']))
                        )
                except Exception as e:
                    logger.warning(f"Skipping invalid trip: {e}")
                    continue
            
            logger.info(f"Loaded {len(trips)} trips")
            
            # Commit all changes
            self.conn.commit()
            logger.info("Data loading complete - all changes committed")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Database error during loading: {e}")
            raise
    
    def run(self, chunksize=10000, init_db=False):
        """
        Run the complete ETL pipeline
        
        Args:
            chunksize: Number of rows to process at a time
            init_db: Whether to initialize database schema
        """
        try:
            logger.info("=" * 50)
            logger.info("Starting ETL Pipeline")
            logger.info("=" * 50)
            
            # Connect to database
            self.connect_db()
            
            # Initialize database if requested
            if init_db:
                self.init_database()
            
            # Process data in chunks
            total_processed = 0
            for chunk in self.extract_data(chunksize):
                # Transform
                transformed = self.transform_data(chunk)
                
                # Load
                self.load_data(transformed)
                
                total_processed += len(chunk)
                logger.info(f"Total rows processed: {total_processed}")
            
            logger.info("=" * 50)
            logger.info("ETL Pipeline Completed Successfully")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise
        finally:
            self.close_db()


def main():
    """Main entry point"""
    # Configuration
    CSV_FILE = 'data.csv'  # Update this to your CSV file path
    DB_FILE = 'database.db'
    CHUNK_SIZE = 10000  # Adjust based on your system's memory
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        logger.error(f"CSV file not found: {CSV_FILE}")
        logger.info("Please update the CSV_FILE path in the script")
        return
    
    # Create and run ETL pipeline
    etl = UrbanMobilityETL(db_path=DB_FILE, csv_path=CSV_FILE)
    etl.run(chunksize=CHUNK_SIZE, init_db=True)


if __name__ == '__main__':
    main()
