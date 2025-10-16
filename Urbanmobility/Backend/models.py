from datetime import datetime
from Urbanmobility.Backend import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Index, CheckConstraint 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Location(db.Model):
    location_id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    __table_args__ = (
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='check_longitude_range'),
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='check_latitude_range'),
        Index('idx_location_coords', 'latitude', 'longitude'),
    )

    def __repr__(self):
        return f"Location('{self.latitude}', '{self.longitude}')"
    
    def validate(self):
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")

class Vendor(db.Model):
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __repr__(self):
        return f"Vendor('{self.vendor_name}')"

class Trip(db.Model):
    trip_id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.vendor_id'), nullable=False)
    pickup_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)
    dropoff_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)
    pickup_datetime = db.Column(db.DateTime, nullable=False)
    dropoff_datetime = db.Column(db.DateTime, nullable=False)
    passenger_count = db.Column(db.Integer, nullable=False)
    trip_distance = db.Column(db.Float, nullable=False)
    store_and_fwd_flag = db.Column(db.String(1), nullable=False)
    fare_amount = db.Column(db.Float, nullable=False)
    trip_duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    __table_args__ = (
        CheckConstraint('passenger_count >= 0', name='check_passenger_count'),
        CheckConstraint('trip_duration > 0', name='check_trip_duration'),
        CheckConstraint('pickup_datetime < dropoff_datetime', name='check_datetime_order'),
        Index('idx_trip_vendor_id', 'vendor_id'),
        Index('idx_trip_pickup_location', 'pickup_location_id'),
        Index('idx_trip_dropoff_location', 'dropoff_location_id'),
        Index('idx_trip_pickup_datetime', 'pickup_datetime'),
        Index('idx_trip_dropoff_datetime', 'dropoff_datetime'),
    )

    def __repr__(self):
        return f"Trip('{self.trip_id}', '{self.vendor_id}', '{self.pickup_location_id}', '{self.dropoff_location_id}')"
    
    def validate(self):
        if self.passenger_count < 0:
            raise ValueError("Passenger count cannot be negative")
        
        if self.trip_duration is not None and self.trip_duration <= 0:
            raise ValueError("Trip duration must be positive")
        
        if self.pickup_datetime >= self.dropoff_datetime:
            raise ValueError("Pickup datetime must be before dropoff datetime")
        
        if self.store_and_fwd_flag not in ['Y', 'N']:
            raise ValueError("Store and forward flag must be 'Y' or 'N'")
    
    def calculate_duration(self):
        if self.pickup_datetime and self.dropoff_datetime:
            delta = self.dropoff_datetime - self.pickup_datetime
            self.trip_duration = int(delta.total_seconds())
        return self.trip_duration
