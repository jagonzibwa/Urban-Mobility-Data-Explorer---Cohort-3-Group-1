"""
ETL Script for Urban Mobility Data Explorer
Extracts data from CSV, Transforms it, and Loads into SQLite database
Robust version that handles variant CSV schemas and generates location IDs
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import logging
import zlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UrbanMobilityETL:
    """ETL pipeline for urban mobility trip data"""
    
    def __init__(self, db_path='instance/site.db', csv_path='train.csv'):
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
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info("Connected to database: %s", self.db_path)
        except sqlite3.Error as e:
            logger.error("Database connection error: %s", e)
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_database(self):
        """Initialize database schema from sqlite_schema.sql (or database.sql as fallback)"""
        try:
            # Prefer SQLite-compatible schema
            schema_file = 'sqlite_schema.sql' if os.path.exists('sqlite_schema.sql') else 'database.sql'
            if schema_file == 'database.sql':
                logger.warning("Using database.sql (MySQL-style); prefer sqlite_schema.sql for SQLite")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor = self.conn.cursor()
            cursor.executescript(schema_sql)
            self.conn.commit()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error("Error initializing database: %s", e)
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
            logger.info("Starting data extraction from %s", self.csv_path)
            
            # Read CSV in chunks to handle large files
            for chunk_num, chunk in enumerate(pd.read_csv(
                self.csv_path, 
                chunksize=chunksize,
                low_memory=False
            ), 1):
                logger.info("Extracted chunk %d with %d rows", chunk_num, len(chunk))
                yield chunk
                
        except FileNotFoundError:
            logger.error("CSV file not found: %s", self.csv_path)
            raise
        except Exception as e:
            logger.error("Error extracting data: %s", e)
            raise
    
    def transform_data(self, df):
        """
        Transform and clean the data - robust version that handles variant CSV schemas
        
        Args:
            df: Raw DataFrame from CSV
            
        Returns:
            Dictionary containing transformed dataframes for each table
        """
        logger.info("Starting data transformation")
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Normalize datetime column names (handle variants)
        datetime_mapping = {
            'tpep_pickup_datetime': 'pickup_datetime',
            'lpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'lpep_dropoff_datetime': 'dropoff_datetime',
        }
        df.rename(columns=datetime_mapping, inplace=True)
        
        # Handle missing values
        df = df.dropna(subset=['pickup_datetime', 'dropoff_datetime'])
        
        # Convert datetime columns
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
        
        # Normalize vendor_id (handle variants)
        if 'VendorID' in df.columns:
            df['vendor_id'] = df['VendorID']
        elif 'vendor_id' not in df.columns:
            df['vendor_id'] = 0
        
        # Normalize passenger_count
        if 'passenger_count' not in df.columns:
            df['passenger_count'] = 1
        df['passenger_count'] = pd.to_numeric(df['passenger_count'], errors='coerce').fillna(1).astype(int)
        
        # Detect coordinate columns (handle variants)
        coord_mapping = {
            'pickup_longitude': ['pickup_longitude', 'start_lon', 'pickup_lon'],
            'pickup_latitude': ['pickup_latitude', 'start_lat', 'pickup_lat'],
            'dropoff_longitude': ['dropoff_longitude', 'end_lon', 'dropoff_lon'],
            'dropoff_latitude': ['dropoff_latitude', 'end_lat', 'dropoff_lat']
        }
        
        for standard_name, variants in coord_mapping.items():
            for variant in variants:
                if variant in df.columns and standard_name not in df.columns:
                    df[standard_name] = df[variant]
                    break
        
        # Generate location IDs from coordinates if not present
        def generate_location_id(lon, lat):
            """Generate stable location ID from coordinates using CRC32"""
            if pd.isna(lon) or pd.isna(lat):
                return None
            # Round to 4 decimal places (~11m precision) and hash
            coord_str = f"{round(float(lon), 4)}_{round(float(lat), 4)}"
            return zlib.crc32(coord_str.encode()) & 0x7FFFFFFF  # Ensure positive
        
        # Check if location ID columns exist, if not generate them
        if 'pickup_location_id' not in df.columns or 'PULocationID' in df.columns:
            if 'PULocationID' in df.columns:
                df['pickup_location_id'] = df['PULocationID']
            else:
                df['pickup_location_id'] = df.apply(
                    lambda row: generate_location_id(row.get('pickup_longitude'), row.get('pickup_latitude')),
                    axis=1
                )
        
        if 'dropoff_location_id' not in df.columns or 'DOLocationID' in df.columns:
            if 'DOLocationID' in df.columns:
                df['dropoff_location_id'] = df['DOLocationID']
            else:
                df['dropoff_location_id'] = df.apply(
                    lambda row: generate_location_id(row.get('dropoff_longitude'), row.get('dropoff_latitude')),
                    axis=1
                )
        
        # Drop rows with missing location IDs
        df = df.dropna(subset=['pickup_location_id', 'dropoff_location_id'])
        
        # Calculate trip duration in seconds if not present
        if 'trip_duration' not in df.columns:
            df['trip_duration'] = (
                df['dropoff_datetime'] - df['pickup_datetime']
            ).dt.total_seconds().astype(int)

        if 'trip_distance' not in df.columns:
            # Check for variant column names
            distance_variants = ['distance', 'trip_dist', 'total_distance']
            for variant in distance_variants:
                if variant in df.columns:
                    df['trip_distance'] = df[variant]
                    break
            
            # If still not found, calculate from coordinates if available
            if 'trip_distance' not in df.columns:
                if all(col in df.columns for col in ['pickup_longitude', 'pickup_latitude', 
                                                    'dropoff_longitude', 'dropoff_latitude']):
                    # Calculate haversine distance
                    from math import radians, sin, cos, sqrt, atan2
                    
                    def haversine_distance(lat1, lon1, lat2, lon2):
                        """Calculate distance in miles between two coordinates"""
                        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
                            return None
                        
                        R = 3959.87433  # Earth's radius in miles
                        
                        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                        dlat = lat2 - lat1
                        dlon = lon2 - lon1
                        
                        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1-a))
                        
                        return R * c
                    
                    df['trip_distance'] = df.apply(
                        lambda row: haversine_distance(
                            row.get('pickup_latitude'), row.get('pickup_longitude'),
                            row.get('dropoff_latitude'), row.get('dropoff_longitude')
                        ),
                        axis=1
                    )
                else:
                    # Default to 0 if no way to calculate (this might not be ideal)
                    logger.warning("trip_distance column missing and cannot be calculated. Using default value of 0.")
                    df['trip_distance'] = 0.0

        # Ensure trip_distance is numeric and handle missing values
        df['trip_distance'] = pd.to_numeric(df['trip_distance'], errors='coerce').fillna(0.0)

        
        # Remove invalid trips (negative duration or too long)
        df = df[
            (df['trip_duration'] > 0) & 
            (df['trip_duration'] < 86400) &  # Less than 24 hours
            (df['trip_distance'] >= 0) &
            (df['trip_distance'] < 500)
        ]
        
        # Extract and create Vendor data
        vendors = df[['vendor_id']].drop_duplicates()
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
        
        # Calculate additional metrics
        # Speed in miles per hour (mph)
        df['speed_mph'] = df.apply(
            lambda row: (row['trip_distance'] / (row['trip_duration'] / 3600)) 
            if row['trip_duration'] > 0 and row['trip_distance'] > 0 else 0.0, 
            axis=1
        )
        
        # Fare per km - using typical NYC taxi fare structure
        # Base fare + per mile rate (converted to per km)
        def calculate_fare_per_km(distance_miles, duration_seconds):
            """Calculate estimated fare per km using typical NYC taxi rates"""
            if distance_miles <= 0:
                return 0.0
            
            # NYC taxi rates (approximate)
            base_fare = 2.50  # Base fare
            per_mile_rate = 2.50  # Per mile rate
            per_minute_rate = 0.50  # Per minute rate (for slow traffic)
            
            # Convert miles to km
            distance_km = distance_miles * 1.60934
            duration_minutes = duration_seconds / 60
            
            # Calculate total fare
            total_fare = base_fare + (distance_miles * per_mile_rate) + (duration_minutes * per_minute_rate)
            
            # Return fare per km
            return total_fare / distance_km if distance_km > 0 else 0.0
        
        df['fare_per_km'] = df.apply(
            lambda row: calculate_fare_per_km(row['trip_distance'], row['trip_duration']),
            axis=1
        )
        
        # Tip ratio - typical tip percentages based on fare
        def calculate_tip_ratio(fare_per_km, distance_km, speed_mph):
            """Calculate tip ratio based on typical tipping patterns"""
            if distance_km <= 0 or fare_per_km <= 0:
                return 0.0
            
            # Base tip percentage
            base_tip_pct = 0.18  # 18% base tip
            
            # Adjust tip based on speed (higher tip for slower, more patient drivers)
            if speed_mph < 10:  # Very slow traffic
                tip_multiplier = 1.2
            elif speed_mph < 20:  # Slow traffic
                tip_multiplier = 1.1
            elif speed_mph > 50:  # Very fast (possibly reckless)
                tip_multiplier = 0.9
            else:  # Normal speed
                tip_multiplier = 1.0
            
            # Adjust for distance (longer trips might get slightly higher tips)
            if distance_km > 10:  # Long trip
                tip_multiplier *= 1.05
            elif distance_km < 1:  # Very short trip
                tip_multiplier *= 0.95
            
            return base_tip_pct * tip_multiplier
        
        df['tip_ratio'] = df.apply(
            lambda row: calculate_tip_ratio(
                row['fare_per_km'], 
                row['trip_distance'] * 1.60934,  # Convert to km
                row['speed_mph']
            ),
            axis=1
        )
        
        # Prepare Trip data
        trip_columns = [
            'vendor_id', 'pickup_location_id', 'dropoff_location_id',
            'pickup_datetime', 'dropoff_datetime', 'passenger_count',
            'trip_duration', 'trip_distance', 'speed_mph', 'fare_per_km', 'tip_ratio'
        ]
        
        # Add optional column if exists
        if 'store_and_fwd_flag' in df.columns:
            trip_columns.append('store_and_fwd_flag')
        
        trips = df[trip_columns].copy()
        
        # Ensure passenger_count is valid
        trips = trips[trips['passenger_count'] > 0]
        
        logger.info("Transformation complete: %d vendors, %d locations, %d trips",
                   len(vendors), len(locations), len(trips))
        
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
            cursor.execute('BEGIN TRANSACTION')
            
            # Load Vendors
            vendors = transformed_data['vendors']
            for _, vendor in vendors.iterrows():
                try:
                    cursor.execute(
                        """INSERT OR IGNORE INTO Vendor (vendor_id, vendor_name) 
                           VALUES (?, ?)""",
                        (int(vendor['vendor_id']), vendor['vendor_name'])
                    )
                except Exception as e:
                    logger.warning("Skipping vendor %s: %s", vendor['vendor_id'], e)
            logger.info("Loaded %d vendors", len(vendors))

            # Load Locations
            locations = transformed_data['locations']
            for _, location in locations.iterrows():
                try:
                    cursor.execute(
                        """INSERT OR IGNORE INTO Location (location_id, longitude, latitude) 
                           VALUES (?, ?, ?)""",
                        (int(location['location_id']), 
                         float(location['longitude']), 
                         float(location['latitude']))
                    )
                except Exception as e:
                    logger.warning("Skipping location %s: %s", location['location_id'], e)
            logger.info("Loaded %d locations", len(locations))

            # Load Trips
            trips = transformed_data['trips']
            for _, trip in trips.iterrows():
                try:
                    if 'store_and_fwd_flag' in trip:
                        cursor.execute(
                            """INSERT INTO Trip 
                                   (vendor_id, pickup_location_id, dropoff_location_id,
                                    pickup_datetime, dropoff_datetime, passenger_count,
                                    store_and_fwd_flag, trip_duration, trip_distance,
                                    speed_mph, fare_per_km, tip_ratio)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (int(trip['vendor_id']),
                             int(trip['pickup_location_id']),
                             int(trip['dropoff_location_id']),
                             trip['pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             trip['dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             int(trip['passenger_count']),
                             trip['store_and_fwd_flag'],
                             int(trip['trip_duration']),
                             float(trip['trip_distance']),
                             float(trip['speed_mph']),
                             float(trip['fare_per_km']),
                             float(trip['tip_ratio']))
                        )
                    else:
                        cursor.execute(
                            """INSERT INTO Trip 
                                   (vendor_id, pickup_location_id, dropoff_location_id,
                                    pickup_datetime, dropoff_datetime, passenger_count,
                                    trip_duration, trip_distance, speed_mph, fare_per_km, tip_ratio)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (int(trip['vendor_id']),
                             int(trip['pickup_location_id']),
                             int(trip['dropoff_location_id']),
                             trip['pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             trip['dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                             int(trip['passenger_count']),
                             int(trip['trip_duration']),
                             float(trip['trip_distance']),
                             float(trip['speed_mph']),
                             float(trip['fare_per_km']),
                             float(trip['tip_ratio']))
                        )
                except Exception as e:
                    logger.warning("Skipping invalid trip: %s", e)
                    continue
            logger.info("Loaded %d trips", len(trips))

            # Commit all changes for this chunk
            self.conn.commit()
            logger.info("Data loading complete - all changes committed for this chunk")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error("Database error during loading: %s", e)
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
                logger.info("Total rows processed: %d", total_processed)

            # For testing, only process one chunk
            # for i, chunk in enumerate(self.extract_data(chunksize)):
            #     transformed = self.transform_data(chunk)
            #     self.load_data(transformed)
            #     total_processed += len(chunk)
            #     logger.info("Total rows processed: %d", total_processed)

            #     # Stop after the first chunk (for testing)
            #     if i == 0:
            #         break
            
            logger.info("=" * 50)
            logger.info("ETL Pipeline Completed Successfully")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error("ETL pipeline failed: %s", e)
            raise
        finally:
            self.close_db()


def main():
    """Main entry point"""
    # Configuration
    CSV_FILE = 'train.csv'  # Update this to your CSV file path
    DB_FILE = 'instance/site.db'
    CHUNK_SIZE = 10000  # Adjust based on your system's memory
    # CHUNK_SIZE = 100
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        logger.error("CSV file not found: %s", CSV_FILE)
        logger.info("Please update the CSV_FILE path in the script")
        return
    
    # Create and run ETL pipeline
    etl = UrbanMobilityETL(db_path=DB_FILE, csv_path=CSV_FILE)
    etl.run(chunksize=CHUNK_SIZE, init_db=False)


if __name__ == '__main__':
    main()