-- SQLite Schema for Urban Mobility Data Explorer
-- Compatible with SQLite (no AUTO_INCREMENT, uses AUTOINCREMENT)

-- Vendor Table
CREATE TABLE IF NOT EXISTS Vendor (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

-- Location Table  
CREATE TABLE IF NOT EXISTS Location (
    location_id INTEGER PRIMARY KEY,
    longitude REAL NOT NULL,
    latitude REAL NOT NULL
);

-- Trip Table
CREATE TABLE IF NOT EXISTS Trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    pickup_datetime TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,
    passenger_count INTEGER NOT NULL,
    store_and_fwd_flag TEXT,
    trip_duration INTEGER NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id),
    FOREIGN KEY (pickup_location_id) REFERENCES Location(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES Location(location_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trip_vendor ON Trip(vendor_id);
CREATE INDEX IF NOT EXISTS idx_trip_pickup_location ON Trip(pickup_location_id);
CREATE INDEX IF NOT EXISTS idx_trip_dropoff_location ON Trip(dropoff_location_id);
CREATE INDEX IF NOT EXISTS idx_trip_pickup_datetime ON Trip(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trip_dropoff_datetime ON Trip(dropoff_datetime);
