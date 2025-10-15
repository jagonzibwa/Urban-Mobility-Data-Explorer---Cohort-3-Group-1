# ETL Script Guide

## Overview
This ETL (Extract, Transform, Load) script processes urban mobility data from CSV files and loads it into your SQLite database.

## Features
- ✅ Handles **variant CSV schemas** (NYC Taxi Yellow/Green, etc.)
- ✅ Generates location IDs from coordinates if missing

## Prerequisites

1. **Python 3.7+** installed
2. **Required packages**: Install using pip
   ```powershell
    py -3 -m pip install --user pandas
   ```

## CSV File Format

The script is **robust** and handles variant CSV schemas automatically. It supports:

### DateTime Columns (any variant):
- `pickup_datetime`, `tpep_pickup_datetime`, or `lpep_pickup_datetime`
- `dropoff_datetime`, `tpep_dropoff_datetime`, or `lpep_dropoff_datetime`

### Coordinate Columns (any variant):
- Pickup: `pickup_longitude/latitude`, `start_lon/lat`, `pickup_lon/lat`
- Dropoff: `dropoff_longitude/latitude`, `end_lon/lat`, `dropoff_lon/lat`

### Location IDs (auto-generated if missing):
- `pickup_location_id` or `PULocationID` (or generated from coordinates)
- `dropoff_location_id` or `DOLocationID` (or generated from coordinates)

### Other Columns:
- `vendor_id` or `VendorID` - Vendor identifier (defaults to 0 if missing)
- `passenger_count` - Number of passengers (defaults to 1 if missing)

### Optional Columns:

## Usage

### Step 1: Prepare Your Data
Place your CSV file in the project directory and name it `train.csv`, or update the `CSV_FILE` variable in the script.

### Step 2: Run the Script
```powershell
py -3 etl_script.py
```

### Step 3: Monitor Progress
The script will display progress logs showing:

## Configuration

Edit these variables in the `main()` function of `etl_script.py`:

```python
CSV_FILE = 'train.csv'     # Path to your CSV file
DB_FILE = 'database.db'    # Output SQLite database file
CHUNK_SIZE = 10000         # Rows to process at once (adjust for memory)
```

### Database Schema
The script uses `sqlite_schema.sql` (SQLite-compatible) if present, otherwise falls back to `database.sql` (MySQL-style with warnings).

### Memory Optimization
If you encounter memory issues with large files:

## Data Validation

The script automatically:
- Normalizes variant column names across different CSV schemas
- Generates stable location IDs from coordinates when needed

## Troubleshooting

### "CSV file not found"
- Update the `CSV_FILE` path in the script to `train.csv`

### "ModuleNotFoundError: No module named 'pandas'"
Install pandas for your user:
```powershell
py -3 -m pip install --user pandas
```

### "Memory Error"

### "Foreign Key Constraint Failed"
- Foreign keys are enabled via `PRAGMA foreign_keys = ON`

### "Date Parsing Error"

### "Schema initialization failed"
- Ensure `sqlite_schema.sql` exists for SQLite compatibility
- Check file encoding is UTF-8

## Example CSV Sample

```csv
VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude,store_and_fwd_flag
2,2016-01-01 00:00:00,2016-01-01 00:15:00,1,-73.9857,40.7484,-73.9744,40.7505,N
1,2016-01-01 00:00:00,2016-01-01 00:30:00,2,-73.9900,40.7500,-73.9600,40.7700,N
```

**Note**: Location IDs will be auto-generated from coordinates in this example.

## Database Output

The script creates/updates three tables:

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

## Notes

- The script defaults to using `train.csv` and outputs to `database.db`
- SQLite database files (*.db) are automatically ignored by Git via `.gitignore`
- Location IDs are generated using CRC32 hash of rounded coordinates for consistency
- The script uses lazy logging formatting for better performance

## Support

For issues or questions, check:
- Database schema in `sqlite_schema.sql` (SQLite) or `database.sql` (MySQL reference)
