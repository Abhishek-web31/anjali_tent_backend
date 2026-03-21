from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

# Admin Schemas
class AdminBase(BaseModel):
    name: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminDisplay(AdminBase):
    id: int
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

# Client Schemas
class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    password: str

class ClientDisplay(ClientBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    client_id: int

class NotificationDisplay(NotificationBase):
    id: int
    client_id: int
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryBase(BaseModel):
    name: str
    category: str
    total_quantity: int
    rent_per_day: int = 0
    description: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryDisplay(InventoryBase):
    id: int
    available_quantity: int
    class Config:
        from_attributes = True

# Contact Inquiry Schemas
class InquiryBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    service: str
    message: str

class InquiryCreate(InquiryBase):
    pass

class InquiryDisplay(InquiryBase):
    id: int
    is_resolved: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Rental Schemas
class RentalBase(BaseModel):
    item_id: int
    quantity: int
    rented_date: date
    expected_return_date: date
    notes: Optional[str] = None

class RentalUpdate(BaseModel):
    returned_quantity: Optional[int] = None
    notes: Optional[str] = None

class RentalCreate(RentalBase):
    booking_id: int

class RentalDisplay(RentalBase):
    id: int
    returned_quantity: int
    is_returned: bool
    notes: Optional[str] = None
    booking_id: int
    item: InventoryDisplay
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    booking_id: int
    amount: int
    payment_method: str = "Cash"
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentDisplay(PaymentBase):
    id: int
    payment_date: datetime
    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    event_date: date
    venue: str
    event_type: str

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    total_amount: Optional[int] = None
    paid_amount: Optional[int] = None

class BookingCreate(BookingBase):
    client_id: int

class BookingDisplay(BookingBase):
    id: int
    client_id: int
    status: str
    total_amount: int
    paid_amount: int
    created_at: datetime
    client: ClientDisplay
    rentals: List[RentalDisplay] = []
    payments: List[PaymentDisplay] = []
    class Config:
        from_attributes = True

# Media Schemas
class MediaBase(BaseModel):
    url: str
    public_id: str
    title: str
    category: str
    description: Optional[str] = None

class MediaCreate(MediaBase):
    pass

class MediaDisplay(MediaBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CloudinarySignature(BaseModel):
    signature: str
    timestamp: int
    api_key: str
    cloud_name: str
