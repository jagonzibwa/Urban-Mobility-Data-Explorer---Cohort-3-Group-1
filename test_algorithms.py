"""
Test script for new consolidated algorithms in API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, url):
    """Test a single API endpoint"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print('-'*60)
        
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            print("✓ SUCCESS")
        else:
            print(f"Error: {response.text}")
            print("✗ FAILED")
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {str(e)}")
        print("✗ ERROR")

def main():
    print("="*60)
    print("TESTING NEW CONSOLIDATED ALGORITHMS")
    print("="*60)
    
    # Test 1: New percentile endpoint (uses QuickSelect)
    test_endpoint(
        "Percentile Calculation (QuickSelect)",
        f"{BASE_URL}/api/stats/percentile?field=trip_duration&p=95"
    )
    
    # Test 2: Vendor performance (uses find_top_k with MinHeap)
    test_endpoint(
        "Vendor Performance (Top-K with MinHeap)",
        f"{BASE_URL}/api/chart/vendor_performance"
    )
    
    # Test 3: Speed anomalies (uses detect_outliers_iqr)
    test_endpoint(
        "Speed Anomalies (IQR Outlier Detection)",
        f"{BASE_URL}/api/anomalies/speed"
    )
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    
    print("\nAlgorithm Mapping:")
    print("1. /api/stats/percentile → QuickSelect (O(n) average)")
    print("2. /api/chart/vendor_performance → MinHeap Top-K (O(n log k))")
    print("3. /api/anomalies/speed → IQR Outlier Detection (O(n))")
    print("\nAll algorithms implemented manually in custom_algorithms.py")

if __name__ == "__main__":
    main()
