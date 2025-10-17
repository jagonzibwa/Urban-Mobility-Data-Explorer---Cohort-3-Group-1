from flask import request, jsonify, render_template, flash, redirect, url_for
from Urbanmobility.Backend import app, db, bcrypt
from Urbanmobility.Backend.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required

from Urbanmobility.Backend.models import User,Location,Vendor,Trip

import json
import os
import sqlite3
from collections import Counter
from datetime import datetime


DB_PATH = 'instance/site.db'

# Load JSON 
json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'urban_mobility_data.json')
with open(json_path, 'r') as f:
    mobility_data = json.load(f)


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

#API endpoints for all my charts 

@app.route('/api/chart/duration_distribution')
def duration_distribution():
    passenger = request.args.get('passenger', 'all')
    query = "SELECT passenger_count, trip_duration FROM trips"
    results = query_db(query)

    def match(p):
        return (
            passenger == 'all' or
            (passenger == '1' and p == 1) or
            (passenger == '2' and p == 2) or
            (passenger == '3+' and p >= 3)
        )
    
    durations = [
        min(int(row['trip_duration']) // 60, 60)
        for row in results if match(row['passenger_count'])
    ]
    counts = Counter(durations)

    return jsonify({
        'labels': [f"{i} min" for i in range(61)],
        'data': [counts.get(i, 0) for i in range(61)]
    })

@app.route('/api/chart/hourly_trips')
def hourly_trips():
    time_of_day = request.args.get('time', 'all')
    query = "SELECT pickup_datetime FROM trips"
    results = query_db(query)

    def in_range(hour):
        return (
            time_of_day == 'all' or
            (time_of_day == 'morning' and 6 <= hour < 12) or
            (time_of_day == 'afternoon' and 12 <= hour < 18) or
            (time_of_day == 'evening' and 18 <= hour < 24) or
            (time_of_day == 'night' and (0 <= hour < 6))
        )
    
    hours = [
        datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').hour
        for row in results
        if in_range(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').hour)
    ]
    counts = Counter(hours)

    return jsonify({
        'labels': list(range(24)),
        'data': [counts.get(h, 0) for h in range(24)]
    })

@app.route('/api/chart/vendor_performance')
def vendor_performance():
    vendor = request.args.get('vendor', 'all')
    query = "SELECT vendor_id, trip_distance FROM trips"
    results = query_db(query)

    filtered = [
        row for row in results
        if vendor == 'all' or str(row['vendor_id']) == vendor
    ]

    vendor_stats = Counter()
    for row in filtered:
        vendor_stats[row['vendor_id']] += row['trip_distance']

    return jsonify({
        'labels': [f"Vendor {v}" for v in vendor_stats.keys()],
        'data': [vendor_stats[v] for v in vendor_stats.keys()]
    })

@app.route('/api/heatmap')
def heatmap():
    location_type = request.args.get('type', 'pickup')
    location_field ='pickup_location_id' if location_type == 'pickup' else 'dropoff_location_id'

    query = f"""
        SELECT L.latitude, L.longitude
        FROM trips T
        JOIN locations L ON T.{location_field} = L.location_id
        WHERE L.latitude is NOT NULL AND L.longitude is NOT NULL
    """

    results = query_db(query)
    return jsonify([[row['latitude'], row['longitude']] for row in results])

    