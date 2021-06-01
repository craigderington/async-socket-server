from database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
# Define application Bases


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)
    active = Column(Boolean, default=1)
    email = Column(String(120), unique=True, nullable=False)
    last_login = Column(DateTime)
    login_count = Column(Integer)
    fail_login_count = Column(Integer)
    created_on = Column(DateTime, default=datetime.now, nullable=True)
    changed_on = Column(DateTime, default=datetime.now, nullable=True)
    created_by_fk = Column(Integer)
    changed_by_fk = Column(Integer)

    def __init__(self, first_name, last_name, username, password, email):
        self.username = username
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return int(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        if self.last_name and self.first_name:
            return "{} {}".format(
                self.first_name,
                self.last_name
            )


class RadioData(Base):
    __tablename__ = "radiodata"
    id = Column(Integer, primary_key=True)
    imei = Column(String(10), nullable=False)
    voltage = Column(Integer)
    rssi = Column(String(10), nullable=False)
    sensorval_1 = Column(String(10), nullable=True)
    sensorval_2 = Column(String(10), nullable=True)
    sensorval_3 = Column(String(10), nullable=True)
    sensorval_4 = Column(String(10), nullable=True)
    created_on = Column(DateTime, default=datetime.now, nullable=True)
    modified_on = Column(DateTime, default=datetime.now, nullable=True)
    sync = Column(Boolean, default=0)
    mcu_ver = Column(String(10), nullable=True)
    firmware_ver = Column(String(10), nullable=True)

    def __repr__(self):
        if self.id is not None:
            return "{} {} {}".format(self.imei, self.voltage, self.sensorval_1)
    
    def get_sensor_value_one(self):
        if self.id and self.sensorval_1:
            return "{}".format(self.sensorval_1)
    
    def get_firmware_version(self):
        if self.id:
            return "{}".format(self.firmware_ver)
    
    def get_mcu_version(self):
        if self.id and self.mcu_version:
            return "{}".format(self.mcu_ver)
    

class OTAUpdate(Base):
    __tablename__ = 'otaupdate'
    id = Column(Integer, primary_key=True)
    ota_path = Column(String(255), nullable=False)
    last_ota_date = Column(DateTime, default=datetime.now, nullable=True)

    def __repr__(self):
        if self.id and self.ota_path:
            return "{}".format(self.ota_path)


