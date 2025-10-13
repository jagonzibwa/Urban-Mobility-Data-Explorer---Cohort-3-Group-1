-- Create the users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Create the Location table
CREATE TABLE Location (
    location_id INTEGER PRIMARY KEY,
    longitude INTEGER NOT NULL,
    latitude INTEGER NOT NULL
);

-- Create the Vendor table
CREATE TABLE Vendor (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the trip table
CREATE TABLE Trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count INTEGER NOT NULL,
    store_and_fwd_flag TEXT,
    trip_duration INTEGER NOT NULL, -- in seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vendor_id) REFERENCES Vendor(Trip),
    FOREIGN KEY (pickup_location_id) REFERENCES Location(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES Location(location_id)
);