DROP TABLE IF EXISTS Trip;
DROP TABLE IF EXISTS Vendor;
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS Users;

-- Users table
CREATE TABLE Users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Location table
CREATE TABLE Location (
  location_id INTEGER PRIMARY KEY AUTOINCREMENT,
  longitude REAL NOT NULL,
  latitude REAL NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CHECK (longitude BETWEEN -180 AND 180),
  CHECK (latitude BETWEEN -90 AND 90)
);

-- Vendor table
CREATE TABLE Vendor (
  vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
  vendor_name TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trip table
CREATE TABLE Trip (
  trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
  vendor_id INTEGER NOT NULL,
  pickup_location_id INTEGER NOT NULL,
  dropoff_location_id INTEGER NOT NULL,
  pickup_datetime TEXT NOT NULL,
  dropoff_datetime TEXT NOT NULL,
  passenger_count INTEGER NOT NULL,
  store_and_fwd_flag TEXT DEFAULT 'N',
  trip_duration INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id),
  FOREIGN KEY (pickup_location_id) REFERENCES Location(location_id),
  FOREIGN KEY (dropoff_location_id) REFERENCES Location(location_id),
  CHECK (passenger_count >= 0),
  CHECK (trip_duration > 0),
  CHECK (datetime(pickup_datetime) < datetime(dropoff_datetime))
);

CREATE INDEX IF NOT EXISTS idx_trip_vendor_id ON Trip(vendor_id);
CREATE INDEX IF NOT EXISTS idx_trip_pickup_location ON Trip(pickup_location_id);
CREATE INDEX IF NOT EXISTS idx_trip_dropoff_location ON Trip(dropoff_location_id);
CREATE INDEX IF NOT EXISTS idx_trip_pickup_datetime ON Trip(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trip_dropoff_datetime ON Trip(dropoff_datetime);
CREATE INDEX IF NOT EXISTS idx_location_coords ON Location(latitude, longitude);