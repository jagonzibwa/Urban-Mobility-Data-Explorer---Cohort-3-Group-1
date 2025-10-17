from flask import request, jsonify, render_template, flash, redirect, url_for, send_from_directory
from Urbanmobility.Backend import app, db, bcrypt
from Urbanmobility.Backend.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required

from Urbanmobility.Backend.models import User,Location,Vendor,Trip
from Urbanmobility.Backend.utils import merge_sort, detect_anomalies_zscore

import json
import os
import sqlite3
from collections import Counter
from datetime import datetime


DB_PATH = 'instance/site.db'

# Load JSON (optional; don't fail if missing)
json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'urban_mobility_data.json')
try:
    with open(json_path, 'r') as f:
        mobility_data = json.load(f)
except FileNotFoundError:
    mobility_data = {}


def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (dict(rv[0]) if rv else None) if one else [dict(row) for row in rv]




# @app.route('/api/trips')
@app.route('/')
@app.route('/home')
@login_required 
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
                        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get('next')
            flash('Login Successful!', 'success') 
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout ():
    logout_user()
    return redirect(url_for('home'))

# Frontend route - serve the main dashboard
@app.route('/dashboard')
def dashboard():
    """Serve the frontend dashboard"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Frontend', 'public')
    return send_from_directory(frontend_path, 'index.html')

# Static file routes for frontend assets
@app.route('/<path:filename>')
def frontend_static(filename):
    """Serve static files from frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Frontend', 'public')
    return send_from_directory(frontend_path, filename)

# API endpoints for all charts

@app.route('/api/chart/hourly_density')
def hourly_density():
    """Get trip density by hour - matches frontend expectation"""
    time_of_day = request.args.get('time', 'all')
    query = "SELECT pickup_datetime FROM Trip"
    results = query_db(query)

    def in_range(hour):
        return (
            time_of_day == 'all' or
            (time_of_day == 'morning' and 6 <= hour < 12) or
            (time_of_day == 'afternoon' and 12 <= hour < 18) or
            (time_of_day == 'evening' and 18 <= hour < 24) or
            (time_of_day == 'night' and (0 <= hour < 6))
        )
    
    hours = []
    for row in results:
        try:
            hour = datetime.strptime(row['pickup_datetime'], '%Y-%m-%d %H:%M:%S').hour
            if in_range(hour):
                hours.append(hour)
        except (ValueError, TypeError):
            continue
    
    counts = Counter(hours)
    
    return jsonify({
        'data': [counts.get(h, 0) for h in range(24)]
    })

@app.route('/api/chart/duration_distribution')
def duration_distribution():
    """Get trip duration distribution by passenger count"""
    passenger = request.args.get('passenger', 'all')
    query = "SELECT passenger_count, trip_duration FROM Trip WHERE trip_duration > 0"
    results = query_db(query)

    def match(p):
        return (
            passenger == 'all' or
            (passenger == '1' and p == 1) or
            (passenger == '2' and p == 2) or
            (passenger == '3+' and p >= 3)
        )
    
    # Create duration bins: 0-5, 5-10, 10-15, 15-20, 20-30, 30+ minutes
    bins = [0, 5, 10, 15, 20, 30, float('inf')]
    bin_counts = [0] * (len(bins) - 1)
    
    for row in results:
        if match(row['passenger_count']):
            duration_minutes = int(row['trip_duration']) // 60
            for i in range(len(bins) - 1):
                if bins[i] <= duration_minutes < bins[i + 1]:
                    bin_counts[i] += 1
                    break

    return jsonify({
        'labels': ['0–5 min', '5–10 min', '10–15 min', '15–20 min', '20–30 min', '30+ min'],
        'data': bin_counts
    })

@app.route('/api/chart/vendor_performance')
def vendor_performance():
    """Get vendor performance comparison using fare_per_km"""
    vendor = request.args.get('vendor', 'all')
    query = """
        SELECT T.vendor_id, V.vendor_name, T.fare_per_km, T.speed_mph, T.trip_distance
        FROM Trip T
        JOIN Vendor V ON T.vendor_id = V.vendor_id
        WHERE T.fare_per_km > 0 AND T.trip_distance > 0
    """
    results = query_db(query)

    # Filter by vendor if specified
    filtered = [
        row for row in results
        if vendor == 'all' or str(row['vendor_id']) == vendor
    ]

    # Group by vendor and calculate averages
    vendor_stats = {}
    for row in filtered:
        vendor_id = row['vendor_id']
        vendor_name = row['vendor_name'] or f"Vendor {vendor_id}"
        
        if vendor_id not in vendor_stats:
            vendor_stats[vendor_id] = {
                'name': vendor_name,
                'fare_per_km_sum': 0,
                'count': 0,
                'total_distance': 0,
                'avg_speed': 0
            }
        
        vendor_stats[vendor_id]['fare_per_km_sum'] += float(row['fare_per_km'])
        vendor_stats[vendor_id]['count'] += 1
        vendor_stats[vendor_id]['total_distance'] += float(row['trip_distance'])
        vendor_stats[vendor_id]['avg_speed'] += float(row['speed_mph'])

    # Calculate averages and sort descending by avg fare_per_km using manual merge sort
    vendor_pairs = []  # (name, avg_fare)
    for _, stats in vendor_stats.items():
        if stats['count'] > 0:
            avg_fare = round(stats['fare_per_km_sum'] / stats['count'], 2)
            vendor_pairs.append((stats['name'], avg_fare))

    # Sort ascending by avg_fare then reverse for descending
    vendor_pairs = list(reversed(merge_sort(vendor_pairs, key=lambda p: p[1])))

    return jsonify({
        'labels': [name for name, _ in vendor_pairs],
        'data': [avg for _, avg in vendor_pairs]
    })

@app.route('/api/heatmap')
def heatmap():
    """Get pickup/dropoff locations for heatmap visualization"""
    location_type = request.args.get('type', 'pickup')
    location_field = 'pickup_location_id' if location_type == 'pickup' else 'dropoff_location_id'

    query = f"""
        SELECT L.latitude, L.longitude, COUNT(*) as trip_count
        FROM Trip T
        JOIN Location L ON T.{location_field} = L.location_id
        WHERE L.latitude IS NOT NULL AND L.longitude IS NOT NULL
        GROUP BY L.latitude, L.longitude
        ORDER BY trip_count DESC
        LIMIT 1000
    """

    results = query_db(query)
    
    # Format for Leaflet heatmap: [lat, lng, intensity]
    heatmap_data = [
        [float(row['latitude']), float(row['longitude']), int(row['trip_count'])]
        for row in results
    ]
    
    return jsonify(heatmap_data)

@app.route('/api/stats/summary')
def stats_summary():
    """Get overall statistics for the dashboard"""
    queries = {
        'total_trips': "SELECT COUNT(*) as count FROM Trip",
        'total_vendors': "SELECT COUNT(*) as count FROM Vendor", 
        'total_locations': "SELECT COUNT(*) as count FROM Location",
        'avg_trip_duration': "SELECT AVG(trip_duration) as avg FROM Trip WHERE trip_duration > 0",
        'avg_speed': "SELECT AVG(speed_mph) as avg FROM Trip WHERE speed_mph > 0",
        'avg_fare_per_km': "SELECT AVG(fare_per_km) as avg FROM Trip WHERE fare_per_km > 0"
    }
    
    stats = {}
    for key, query in queries.items():
        result = query_db(query, one=True)
        if result:
            stats[key] = round(result['count'] if 'count' in result else result['avg'], 2)
    
    return jsonify(stats)


@app.route('/api/anomalies/speed')
def anomalies_speed():
    """Detect speed anomalies using manual z-score (no numpy/pandas)."""
    try:
        z = float(request.args.get('z', '3.0'))
    except ValueError:
        z = 3.0

    rows = query_db("SELECT speed_mph FROM Trip WHERE speed_mph > 0")
    speeds = [float(r['speed_mph']) for r in rows]
    anomalies = detect_anomalies_zscore(speeds, z_threshold=z)
    # anomalies: list of (index, value, z)
    top = anomalies[:100]
    return jsonify({
        'count': len(anomalies),
        'z_threshold': z,
        'examples': [
            {'index': idx, 'speed_mph': val, 'z': round(zv, 3)} for idx, val, zv in top
        ]
    })

    