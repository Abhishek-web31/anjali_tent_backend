from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="superadmin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bookings = relationship("Booking", back_populates="client")
    notifications = relationship("Notification", back_populates="client")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="notifications")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    event_date = Column(Date, index=True)
    venue = Column(String)
    event_type = Column(String)
    status = Column(String, default="Pending") # Pending, Confirmed, Completed, Cancelled
    total_amount = Column(Integer, default=0)
    paid_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="bookings")
    rentals = relationship("Rental", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Integer)
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    payment_method = Column(String, default="Cash") # Cash, UPI, Bank Transfer
    notes = Column(Text, nullable=True)

    booking = relationship("Booking", back_populates="payments")

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    total_quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)
    rent_per_day = Column(Integer, default=0)
    description = Column(Text, nullable=True)

    rentals = relationship("Rental", back_populates="item")

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    public_id = Column(String)
    title = Column(String)
    category = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    item_id = Column(Integer, ForeignKey("inventory.id"))
    quantity = Column(Integer, default=1)
    returned_quantity = Column(Integer, default=0)
    rented_date = Column(Date)
    expected_return_date = Column(Date)
    is_returned = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    booking = relationship("Booking", back_populates="rentals")
    item = relationship("InventoryItem", back_populates="rentals")

class ContactInquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    service = Column(String)
    message = Column(Text)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
