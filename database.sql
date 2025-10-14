DROP TRIGGER IF EXISTS generate_User_id;
DROP TRIGGER IF EXISTS generate_Location_id;
DROP TRIGGER IF EXISTS generate_Vendor_id;
DROP TRIGGER IF EXISTS generate_Trip_id;

DROP TABLE IF EXISTS `Trip`;
DROP TABLE IF EXISTS `Vendor`;
DROP TABLE IF EXISTS `Location`;
DROP TABLE IF EXISTS `Users`;

DROP TABLE IF EXISTS `Trip_sequence`;
DROP TABLE IF EXISTS `Vendor_sequence`;
DROP TABLE IF EXISTS `Location_sequence`;
DROP TABLE IF EXISTS `Users_sequence`;


CREATE TABLE `Users_sequence` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT
);

CREATE TABLE `Location_sequence` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT
);

CREATE TABLE `Vendor_sequence` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT
);

CREATE TABLE `Trip_sequence` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT
);


-- Users table
CREATE TABLE `Users` (
  id VARCHAR(50) PRIMARY KEY NOT NULL,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CHECK (CHAR_LENGTH(username) > 0),
  CHECK (CHAR_LENGTH(password) > 0)
);

DELIMITER $$
CREATE TRIGGER generate_User_id
BEFORE INSERT ON `Users`
FOR EACH ROW
BEGIN
  INSERT INTO `Users_sequence` VALUES (NULL);
  SET NEW.id = CONCAT('USER', LPAD(LAST_INSERT_ID(), 4, '0'));
END$$
DELIMITER ;

-- Location table
CREATE TABLE `Location` (
  location_id VARCHAR(50) PRIMARY KEY NOT NULL,
  longitude DECIMAL(9,6) NOT NULL,
  latitude DECIMAL(8,6) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CHECK (longitude BETWEEN -180 AND 180),
  CHECK (latitude BETWEEN -90 AND 90)
);

DELIMITER $$
CREATE TRIGGER generate_Location_id
BEFORE INSERT ON `Location`
FOR EACH ROW
BEGIN
  INSERT INTO `Location_sequence` VALUES (NULL);
  SET NEW.location_id = CONCAT('LOC', LPAD(LAST_INSERT_ID(), 4, '0'));
END$$
DELIMITER ;

-- Vendor table
CREATE TABLE `Vendor` (
  vendor_id VARCHAR(50) PRIMARY KEY NOT NULL,
  vendor_name VARCHAR(255) NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER generate_Vendor_id
BEFORE INSERT ON `Vendor`
FOR EACH ROW
BEGIN
  INSERT INTO `Vendor_sequence` VALUES (NULL);
  SET NEW.vendor_id = CONCAT('VEND', LPAD(LAST_INSERT_ID(), 4, '0'));
END$$
DELIMITER ;

-- Trip table
CREATE TABLE `Trip` (
  trip_id VARCHAR(50) PRIMARY KEY NOT NULL,
  vendor_id VARCHAR(50) NOT NULL,
  pickup_location_id VARCHAR(50) NOT NULL,
  dropoff_location_id VARCHAR(50) NOT NULL,
  pickup_datetime DATETIME NOT NULL,
  dropoff_datetime DATETIME NOT NULL,
  passenger_count INT NOT NULL,
  store_and_fwd_flag ENUM('Y','N') DEFAULT 'N',
  trip_duration INT NOT NULL, -- seconds
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_trip_vendor FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id),
  CONSTRAINT fk_trip_pickup_loc FOREIGN KEY (pickup_location_id) REFERENCES Location(location_id),
  CONSTRAINT fk_trip_dropoff_loc FOREIGN KEY (dropoff_location_id) REFERENCES Location(location_id),

  CHECK (passenger_count >= 0),
  CHECK (trip_duration > 0),
  CHECK (pickup_datetime < dropoff_datetime)
);

DELIMITER $$
CREATE TRIGGER generate_Trip_id
BEFORE INSERT ON `Trip`
FOR EACH ROW
BEGIN
  INSERT INTO `Trip_sequence` VALUES (NULL);
  SET NEW.trip_id = CONCAT('TRIP', LPAD(LAST_INSERT_ID(), 6, '0'));
END$$
DELIMITER ;



CREATE INDEX idx_trip_vendor_id ON `Trip`(vendor_id);
CREATE INDEX idx_trip_pickup_location ON `Trip`(pickup_location_id);
CREATE INDEX idx_trip_dropoff_location ON `Trip`(dropoff_location_id);
CREATE INDEX idx_trip_pickup_datetime ON `Trip`(pickup_datetime);
CREATE INDEX idx_trip_dropoff_datetime ON `Trip`(dropoff_datetime);
CREATE INDEX idx_location_coords ON `Location`(latitude, longitude);
