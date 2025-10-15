# ETL Script Guide

## Overview
This ETL (Extract, Transform, Load) script processes urban mobility data from CSV files and loads it into your SQLite database.

## Features
- ✅ Handles **large CSV files** using chunked processing
- ✅ Validates and cleans data automatically
- ✅ Calculates trip duration if not present
- ✅ Removes invalid trips (negative duration, missing data)
- ✅ Extracts unique vendors and locations
- ✅ Comprehensive logging
- ✅ Error handling and recovery

## Prerequisites

1. **Python 3.7+** installed
2. **Required packages**: Install using pip
   ```powershell
   pip install pandas
   ```

## CSV File Format

Your CSV file should have the following columns (column names may vary):

### Required Columns:
- `vendor_id` - Vendor identifier
- `pickup_datetime` - Trip start time
- `dropoff_datetime` - Trip end time
- `pickup_location_id` - Pickup location ID
- `dropoff_location_id` - Dropoff location ID
- `pickup_longitude` - Pickup longitude coordinate
- `pickup_latitude` - Pickup latitude coordinate
- `dropoff_longitude` - Dropoff longitude coordinate
- `dropoff_latitude` - Dropoff latitude coordinate
- `passenger_count` - Number of passengers

### Optional Columns:
- `vendor_name` - Name of the vendor (auto-generated if missing)
- `trip_duration` - Duration in seconds (calculated if missing)
- `store_and_fwd_flag` - Store and forward flag

## Usage

### Step 1: Prepare Your Data
Place your CSV file in the project directory and name it `data.csv`, or update the `CSV_FILE` variable in the script.

### Step 2: Run the Script
```powershell
python etl_script.py
```

### Step 3: Monitor Progress
The script will display progress logs showing:
- Number of rows extracted
- Data transformation progress
- Number of vendors, locations, and trips loaded
- Any errors or warnings

## Configuration

Edit these variables in the `main()` function of `etl_script.py`:

```python
CSV_FILE = 'data.csv'      # Path to your CSV file
DB_FILE = 'database.db'    # Output database file
CHUNK_SIZE = 10000         # Rows to process at once (adjust for memory)
```

### Memory Optimization
If you encounter memory issues with large files:
- Reduce `CHUNK_SIZE` (e.g., 5000 or 1000)
- Process data in smaller batches

## Data Validation

The script automatically:
- Removes trips with missing datetime values
- Filters out negative or zero-duration trips
- Removes trips longer than 24 hours (configurable)
- Ensures passenger count > 0
- Handles duplicate vendors and locations

## Troubleshooting

### "CSV file not found"
- Ensure your CSV file exists in the project directory
- Update the `CSV_FILE` path in the script

### "Memory Error"
- Reduce the `CHUNK_SIZE` parameter
- Close other applications to free up memory

### "Foreign Key Constraint Failed"
- The script loads data in the correct order (Vendors → Locations → Trips)
- Check that your CSV has valid location and vendor IDs

### "Date Parsing Error"
- Ensure datetime columns are in a standard format (e.g., `YYYY-MM-DD HH:MM:SS`)
- The script uses pandas' flexible date parser

## Example CSV Sample

```csv
vendor_id,vendor_name,pickup_datetime,dropoff_datetime,pickup_location_id,dropoff_location_id,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude,passenger_count,store_and_fwd_flag
1,Yellow Cab,2023-01-01 08:00:00,2023-01-01 08:15:00,101,102,-73.9857,40.7484,-73.9744,40.7505,2,N
2,Green Cab,2023-01-01 09:00:00,2023-01-01 09:30:00,103,104,-73.9900,40.7500,-73.9600,40.7700,1,N
```

## Database Output

The script creates/updates three tables:
- `Vendor` - Unique vendors
- `Location` - Unique pickup/dropoff locations
- `Trip` - Individual trip records

## Advanced Usage

### Custom Transformations
Modify the `transform_data()` method to add custom logic:
```python
def transform_data(self, df):
    # Your custom transformations here
    df['custom_field'] = df['some_column'] * 2
    # ... rest of the transformation
```

### Running Without Database Initialization
If your database already exists with the correct schema:
```python
etl.run(chunksize=CHUNK_SIZE, init_db=False)
```

## Performance Tips

For optimal performance with large files:
1. Use SSD storage for database file
2. Adjust chunk size based on available RAM
3. Run during off-peak hours for very large datasets
4. Consider indexing after data load completion

## Support

For issues or questions, check:
- Script logs for detailed error messages
- Database schema in `database.sql`
- This README for configuration options
