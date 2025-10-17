#!/usr/bin/env python3
"""
Integration test script to verify frontend-backend connectivity
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all API endpoints to ensure they work correctly"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/api/stats/summary",
        "/api/chart/hourly_density?time=all",
        "/api/chart/duration_distribution?passenger=all",
        "/api/chart/vendor_performance?vendor=all",
        "/api/heatmap?type=pickup",
        "/api/heatmap?type=dropoff"
    ]
    
    print("Testing API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}")
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
                else:
                    print(f"   Type: {type(data)}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
        print()
    
    # Test frontend serving
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend dashboard serving correctly")
        else:
            print(f"❌ Frontend dashboard - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend dashboard - Error: {e}")

def test_data_quality():
    """Test that the data makes sense"""
    print("\nTesting data quality...")
    print("=" * 50)
    
    try:
        # Test stats endpoint
        response = requests.get("http://localhost:5000/api/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print("📊 Dashboard Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Validate data makes sense
            if stats.get('total_trips', 0) > 0:
                print("✅ Total trips > 0")
            else:
                print("❌ No trips found")
                
            if stats.get('avg_speed', 0) > 0:
                print("✅ Average speed calculated")
            else:
                print("❌ No speed data")
                
            if stats.get('avg_fare_per_km', 0) > 0:
                print("✅ Average fare calculated")
            else:
                print("❌ No fare data")
        
        # Test hourly density
        response = requests.get("http://localhost:5000/api/chart/hourly_density?time=all")
        if response.status_code == 200:
            hourly_data = response.json()
            if 'data' in hourly_data and len(hourly_data['data']) == 24:
                print("✅ Hourly density data has 24 hours")
            else:
                print("❌ Hourly density data incomplete")
        
        # Test vendor performance
        response = requests.get("http://localhost:5000/api/chart/vendor_performance?vendor=all")
        if response.status_code == 200:
            vendor_data = response.json()
            if 'labels' in vendor_data and 'data' in vendor_data:
                print(f"✅ Vendor performance data: {len(vendor_data['labels'])} vendors")
            else:
                print("❌ Vendor performance data incomplete")
                
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Frontend-Backend Integration Test")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    test_api_endpoints()
    test_data_quality()
    
    print("\n" + "=" * 60)
    print("🎉 Integration test completed!")
    print("\nTo view the dashboard, open: http://localhost:5000/dashboard")
    print("To view the login page, open: http://localhost:5000/")
