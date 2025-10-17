#!/usr/bin/env python3
"""
Test script to verify the new calculated columns work correctly
"""

import pandas as pd
import sys
import os

# Add current directory to path to import ETL module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl_script import UrbanMobilityETL

def test_calculations():
    """Test the calculation functions with sample data"""
    
    # Create sample data
    sample_data = pd.DataFrame({
        'vendor_id': [1, 2, 1],
        'pickup_datetime': ['2016-03-14 17:24:55', '2016-06-12 00:43:35', '2016-01-19 11:35:24'],
        'dropoff_datetime': ['2016-03-14 17:32:30', '2016-06-12 00:54:38', '2016-01-19 12:10:48'],
        'passenger_count': [1, 1, 1],
        'pickup_longitude': [-73.982154846191406, -73.980415344238281, -73.979026794433594],
        'pickup_latitude': [40.767936706542969, 40.738563537597656, 40.763938903808594],
        'dropoff_longitude': [-73.964630126953125, -73.999481201171875, -74.005332946777344],
        'dropoff_latitude': [40.765602111816406, 40.731151580810547, 40.710086822509766],
        'store_and_fwd_flag': ['N', 'N', 'N'],
        'trip_duration': [455, 663, 2124]  # seconds
    })
    
    # Convert datetime columns
    sample_data['pickup_datetime'] = pd.to_datetime(sample_data['pickup_datetime'])
    sample_data['dropoff_datetime'] = pd.to_datetime(sample_data['dropoff_datetime'])
    
    print("Sample data:")
    print(sample_data[['vendor_id', 'trip_duration', 'pickup_datetime', 'dropoff_datetime']])
    print()
    
    # Initialize ETL
    etl = UrbanMobilityETL()
    
    # Test transformation
    print("Testing transformation...")
    transformed = etl.transform_data(sample_data)
    
    trips = transformed['trips']
    print("\nTransformed trips data:")
    print(trips[['vendor_id', 'trip_duration', 'trip_distance', 'speed_mph', 'fare_per_km', 'tip_ratio']])
    print()
    
    # Verify calculations
    print("Verification:")
    for idx, trip in trips.iterrows():
        print(f"Trip {idx + 1}:")
        print(f"  Duration: {trip['trip_duration']} seconds ({trip['trip_duration']/60:.1f} minutes)")
        print(f"  Distance: {trip['trip_distance']:.2f} miles")
        print(f"  Speed: {trip['speed_mph']:.2f} mph")
        print(f"  Fare per km: ${trip['fare_per_km']:.2f}")
        print(f"  Tip ratio: {trip['tip_ratio']:.1%}")
        
        # Manual verification of speed calculation
        expected_speed = (trip['trip_distance'] / (trip['trip_duration'] / 3600)) if trip['trip_duration'] > 0 else 0
        print(f"  Expected speed: {expected_speed:.2f} mph")
        print()

if __name__ == '__main__':
    test_calculations()
