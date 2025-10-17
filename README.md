# Urban Mobility Data Explorer

**Team:** Cohort 3 - Group 1

[![Demo Video](https://img.shields.io/badge/Demo-Watch%20on%20YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/_hH4Wj6GL3s)

---

## Project Description

The **Urban Mobility Data Explorer** is a comprehensive full-stack web application designed to analyze and visualize urban transportation patterns using NYC Taxi trip data. This project demonstrates enterprise-level web development practices, combining robust backend processing with interactive frontend visualizations to deliver actionable insights into urban mobility trends.

### Key Features

🔹 **Intelligent ETL Pipeline**
- Automated data extraction, transformation, and loading from large CSV datasets
- Schema-flexible processing supporting multiple taxi data formats (Yellow/Green cabs)
- Memory-efficient chunk-based processing for datasets with millions of records
- Automatic data validation, cleaning, and calculated metrics generation

🔹 **Advanced Data Analytics**
- Custom-built algorithms for performance optimization (no external algorithm libraries)
- Percentile calculation using QuickSelect (O(n) complexity)
- IQR-based outlier detection for identifying speed anomalies
- Top-K selection using Min Heap for vendor performance ranking
- Binary Search Tree for efficient range queries
- Real-time statistical aggregations and insights

🔹 **Interactive Visualizations**
- **Trip Density Analysis**: Line charts showing hourly trip patterns with time-based filtering
- **Duration Distribution**: Bar charts displaying trip duration breakdowns by passenger count
- **Vendor Performance**: Comparative analytics of fare efficiency across vendors
- **Geographic Heatmap**: Interactive Leaflet map with pickup/dropoff location clustering
- Real-time dashboard with key performance indicators

🔹 **RESTful API Architecture**
- Well-structured API endpoints for data retrieval and analytics
- JSON-based responses with proper error handling
- Query parameter support for flexible data filtering
- CORS-enabled for frontend integration

🔹 **User Authentication & Security**
- Flask-Login integration for secure user sessions
- Bcrypt password hashing
- Admin user management system
- Protected routes and role-based access control

🔹 **Responsive Web Interface**
- Modern, mobile-friendly design
- Dynamic chart updates using Chart.js
- Interactive map controls with Leaflet
- Real-time data filtering and visualization updates

### Technical Highlights

- **Backend**: Flask 3.1.2 with SQLAlchemy ORM
- **Database**: SQLite with optimized indexes for fast queries
- **Frontend**: Vanilla JavaScript with Chart.js and Leaflet
- **Data Processing**: Pandas for ETL operations
- **Algorithms**: 9 manually implemented data structures (QuickSelect, MinHeap, BST, Hash Table, etc.)
- **Architecture**: MVC pattern with separation of concerns

### Use Cases

This application serves multiple stakeholders:

- **Urban Planners**: Analyze traffic patterns to optimize infrastructure
- **Transportation Services**: Understand demand patterns for resource allocation
- **Data Analysts**: Explore mobility trends and generate insights
- **Researchers**: Study urban mobility behavior and patterns
- **Business Intelligence**: Monitor vendor performance and operational metrics

### Demo

Watch our comprehensive demo showcasing all features:
**[View Demo on YouTube](https://youtu.be/_hH4Wj6GL3s)**

---

## Initialise Database

```bash
python3 run.py
```

## User Creation

### For Linux/Mac (bash):
```bash
export FLASK_APP=Urbanmobility.Backend
flask create-admin
```

### For Windows (PowerShell):
```powershell
$env:FLASK_APP = "Urbanmobility.Backend"
python -m flask create-admin
```

### For Windows (CMD):
```cmd
set FLASK_APP=Urbanmobility.Backend
python -m flask create-admin
```


Place your CSV file in the project root and name it `train.csv`, or update the path in `etl_script.py`.

**Supported CSV Formats:**
- NYC Taxi Yellow/Green cabs
- Custom mobility data with coordinates
- Any CSV with pickup/dropoff coordinates

### 3. Run ETL Pipeline

```bash
python3 etl_script.py
```

This will:
- Process your CSV data
- Calculate additional metrics (speed, fare/km, tip ratios)
- Load data into SQLite database
- Create optimized indexes

### 4. Start the Application

```bash
python3 run.py
```

### 5. Access the Application

- **Main Dashboard**: http://localhost:5000/dashboard
- **Login Page**: http://localhost:5000/
- **API Documentation**: http://localhost:5000/api/stats/summary

## Project Structure

```
Urban-Mobility-Data-Explorer---Cohort-3-Group-1/
├── Frontend/                    # Frontend assets
│   ├── public/                  # Static files
│   │   ├── index.html             # Main dashboard
│   │   ├── app.js                 # Frontend JavaScript
│   │   └── styles.css             # Styling
│   └── src/                    # Source components
├── Urbanmobility/              # Backend Flask application
│   ├── Backend/                # Core backend
│   │   ├── __init__.py           # Flask app initialization
│   │   ├── models.py             # Database models
│   │   ├── routes.py             # API endpoints
│   │   └── forms.py              # Form definitions
│   └── templates/             # Jinja2 templates
├── instance/                  # Database and runtime files
│   ├── site.db                   # SQLite database
│   ├── extract.py               # Data export utility
│   └── urban_mobility_data.json # JSON data export
├── tests/                     # Test files
├── etl_script.py                # Main ETL pipeline
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── sqlite_schema.sql           # Database schema
└── README.md                   # This file
```

## ETL Pipeline

The ETL (Extract, Transform, Load) pipeline is designed to handle various urban mobility data formats.

### Features

- **Schema Flexibility**: Automatically handles different CSV column naming conventions
- **Data Validation**: Validates and cleans data during transformation
- **Calculated Fields**: Generates speed, fare per km, and tip ratios
- **Location Processing**: Creates stable location IDs from coordinates
- **Memory Efficient**: Processes large files in chunks

### Usage

```bash
# Basic usage
python3 etl_script.py

# With custom parameters (edit in script)
CSV_FILE = 'your_data.csv'
DB_FILE = 'instance/site.db'
CHUNK_SIZE = 10000
```

### Supported CSV Formats

The pipeline automatically detects and handles:

**DateTime Columns:**
- `pickup_datetime`, `tpep_pickup_datetime`, `lpep_pickup_datetime`
- `dropoff_datetime`, `tpep_dropoff_datetime`, `lpep_dropoff_datetime`

**Coordinate Columns:**
- Pickup: `pickup_longitude/latitude`, `start_lon/lat`, `pickup_lon/lat`
- Dropoff: `dropoff_longitude/latitude`, `end_lon/lat`, `dropoff_lon/lat`

**Location IDs:**
- `pickup_location_id`, `PULocationID` (or auto-generated)
- `dropoff_location_id`, `DOLocationID` (or auto-generated)

## API Documentation

### Core Endpoints

#### Statistics Summary
```http
GET /api/stats/summary
```
Returns overall dashboard statistics including total trips, vendors, locations, and averages.

#### Trip Density by Hour
```http
GET /api/chart/hourly_density?time={filter}
```
**Parameters:**
- `time`: `all`, `morning`, `afternoon`, `evening`, `night`

#### Duration Distribution
```http
GET /api/chart/duration_distribution?passenger={count}
```
**Parameters:**
- `passenger`: `all`, `1`, `2`, `3+`

#### Vendor Performance
```http
GET /api/chart/vendor_performance?vendor={id}
```
**Parameters:**
- `vendor`: `all`, `1`, `2`

#### Heatmap Data
```http
GET /api/heatmap?type={location_type}
```
**Parameters:**
- `type`: `pickup`, `dropoff`

### Example API Response

```json
{
  "avg_fare_per_km": 12.24,
  "avg_speed": 9.0,
  "avg_trip_duration": 938.46,
  "total_locations": 373732,
  "total_trips": 40000,
  "total_vendors": 2
}
```

## Frontend Features

### Interactive Charts

1. **Trip Density by Hour**
   - Line chart showing trip patterns throughout the day
   - Time-based filtering (morning, afternoon, evening, night)
   - Real-time updates

2. **Duration Distribution**
   - Bar chart showing trip duration patterns
   - Passenger count filtering
   - Responsive design

3. **Vendor Performance**
   - Comparative bar chart
   - Vendor-specific filtering
   - Average fare per km analysis

4. **Interactive Heatmap**
   - Geographic visualization using Leaflet
   - Toggle between pickup and dropoff locations
   - Color-coded intensity markers
   - Click for detailed information

### Dashboard Statistics

Real-time metrics displayed on the home page:
- Total trips analyzed
- Number of vendors tracked
- Unique locations mapped
- Average trip duration
- Average speed
- Average fare per km

## Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_APP=Urbanmobility.Backend
FLASK_ENV=development  # or production
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///instance/site.db

# Security
SECRET_KEY=your-secret-key-here
```

### ETL Configuration

Edit these variables in `etl_script.py`:

```python
CSV_FILE = 'train.csv'           # Path to your CSV file
DB_FILE = 'instance/site.db'     # Output database path
CHUNK_SIZE = 10000              # Rows to process at once
```

### Frontend Configuration

Update API endpoints in `Frontend/public/app.js` if needed:

```javascript
const API_BASE_URL = 'http://localhost:5000';
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'flask'"
```bash
# Ensure virtual environment is activated
source urbanmobility/bin/activate  # Linux/Mac
# or
urbanmobility\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
```

#### "CSV file not found"
- Ensure your CSV file is named `train.csv` in the project root
- Or update the `CSV_FILE` variable in `etl_script.py`

#### "Database connection error"
```bash
# Check if database file exists
ls instance/site.db

# Recreate database
rm instance/site.db
python3 etl_script.py
```

#### "Port 5000 already in use"
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :5000   # Windows
```

#### Frontend not loading charts
1. Check browser console for errors
2. Verify API endpoints are responding:
   ```bash
   curl http://localhost:5000/api/stats/summary
   ```
3. Ensure Flask app is running in debug mode

#### Heatmap not displaying
- Check if Leaflet library is loading in browser console
- Verify API returns heatmap data:
  ```bash
  curl http://localhost:5000/api/heatmap?type=pickup
  ```

### Performance Issues

#### Large CSV files
- Reduce `CHUNK_SIZE` in `etl_script.py` (try 5000 or 1000)
- Ensure sufficient disk space for database file
- Consider running during off-peak hours

#### Slow API responses
- Check database indexes are created
- Monitor memory usage during ETL process
- Consider database optimization

### Debug Mode

Enable Flask debug mode for detailed error messages:

```bash
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows
python3 run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 .
```

## License

This project is part of a cohort learning program. Please respect the educational context and use appropriately.

## Support

For issues or questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the API documentation
3. Check the browser console for frontend errors
4. Examine Flask application logs

## Project Goals

This Urban Mobility Data Explorer demonstrates:

- **Full-stack Development**: Flask backend with modern frontend
- **Data Processing**: Robust ETL pipeline with error handling
- **API Design**: RESTful endpoints with proper error responses
- **Visualisation**: Interactive charts and geographic mapping
- **User Experience**: Responsive design with real-time updates
- **Production Readiness**: Proper configuration and deployment considerations

---

 
