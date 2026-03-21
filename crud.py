from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- Admin Operations ---
def get_admin_by_email(db: Session, email: str):
    return db.query(models.Admin).filter(models.Admin.email == email).first()

def create_admin(db: Session, admin: schemas.AdminCreate):
    hashed_password = get_password_hash(admin.password)
    db_admin = models.Admin(name=admin.name, email=admin.email, hashed_password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admins(db: Session):
    return db.query(models.Admin).all()

def verify_admin_login(db: Session, login_data: schemas.AdminLogin): # Reusing same schema for simplicity
    admin = get_admin_by_email(db, login_data.email)
    if not admin:
        return None
    if not verify_password(login_data.password, admin.hashed_password):
        return None
    return admin

# --- CLIENT CRUD ---
def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.email == email).first()

def create_client(db: Session, client: schemas.ClientCreate):
    hashed_password = get_password_hash(client.password)
    db_client = models.Client(
        name=client.name, 
        email=client.email, 
        phone=client.phone, 
        address=client.address, 
        hashed_password=hashed_password
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def verify_client_login(db: Session, email: str, password: str):
    client = get_client_by_email(db, email)
    if not client:
        return None
    if not verify_password(password, client.hashed_password):
        return None
    return client

def get_clients(db: Session):
    return db.query(models.Client).all()

# --- NOTIFICATIONS CRUD ---
def create_notification(db: Session, notification: schemas.NotificationCreate):
    db_notif = models.Notification(**notification.dict())
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_client_notifications(db: Session, client_id: int):
    return db.query(models.Notification).filter(models.Notification.client_id == client_id).all()

# --- INVENTORY CRUD ---
def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    db_item = models.InventoryItem(**item.dict(), available_quantity=item.total_quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_inventory(db: Session):
    return db.query(models.InventoryItem).all()

def update_inventory_item(db: Session, item_id: int, item_update: schemas.InventoryCreate):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if db_item:
        for key, value in item_update.dict().items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
        return db_item
    return None

def delete_inventory_item(db: Session, item_id: int):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

# --- BOOKING CRUD ---
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session):
    return db.query(models.Booking).all()

def get_client_bookings(db: Session, client_id: int):
    return db.query(models.Booking).filter(models.Booking.client_id == client_id).all()

def update_booking(db: Session, booking_id: int, booking_update: schemas.BookingUpdate):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        return None
    
    if booking_update.status:
        booking.status = booking_update.status
    if booking_update.total_amount is not None:
        booking.total_amount = booking_update.total_amount
    if booking_update.paid_amount is not None:
        booking.paid_amount = booking_update.paid_amount

    db.commit()
    db.refresh(booking)
    return booking

# --- RENTAL CRUD ---
def create_rental(db: Session, rental: schemas.RentalCreate):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == rental.item_id).first()
    if not item or item.available_quantity < rental.quantity:
        return None 
    
    db_rental = models.Rental(**rental.dict())
    item.available_quantity -= rental.quantity
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    # Auto-calculate bill upon adding rental
    calculate_booking_bill(db, rental.booking_id)
    return db_rental

def get_rentals(db: Session):
    return db.query(models.Rental).all()

def calculate_booking_bill(db: Session, booking_id: int):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        return 0
    
    total = 0
    for rental in booking.rentals:
        # Calculate duration in days
        duration = (rental.expected_return_date - rental.rented_date).days
        if duration <= 0: duration = 1 # Minimum 1 day rent
        
        item_price = rental.item.rent_per_day or 0
        total += (item_price * rental.quantity * duration)
    
    booking.total_amount = total
    db.commit()
    db.refresh(booking)
    return total

def update_rental(db: Session, rental_id: int, rental_update: schemas.RentalUpdate):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        return None

    if rental_update.notes is not None:
        rental.notes = rental_update.notes

    if rental_update.returned_quantity is not None and not rental.is_returned:
        new_return_amt = min(rental_update.returned_quantity, rental.quantity)
        diff = new_return_amt - rental.returned_quantity
        if diff > 0:
            item = db.query(models.InventoryItem).filter(models.InventoryItem.id == rental.item_id).first()
            if item:
                item.available_quantity += diff
            rental.returned_quantity = new_return_amt
            if rental.returned_quantity >= rental.quantity:
                rental.is_returned = True

    db.commit()
    db.refresh(rental)
    return rental

# --- INQUIRY CRUD ---
def create_inquiry(db: Session, inquiry: schemas.InquiryCreate):
    db_inquiry = models.ContactInquiry(**inquiry.dict())
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

def get_inquiries(db: Session):
    return db.query(models.ContactInquiry).all()

def resolve_inquiry(db: Session, inquiry_id: int):
    inquiry = db.query(models.ContactInquiry).filter(models.ContactInquiry.id == inquiry_id).first()
    if inquiry:
        inquiry.is_resolved = True
        db.commit()
        db.refresh(inquiry)
    return inquiry

# --- MEDIA CRUD ---
def create_media(db: Session, media: schemas.MediaCreate):
    db_media = models.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def get_all_media(db: Session):
    return db.query(models.Media).all()

def delete_media(db: Session, media_id: int):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if db_media:
        db.delete(db_media)
        db.commit()
        return True
    return False

def update_media(db: Session, media_id: int, media_update: schemas.MediaCreate):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if db_media:
        for key, value in media_update.dict().items():
            setattr(db_media, key, value)
        db.commit()
        db.refresh(db_media)
        return db_media
    return None

# --- PAYMENT CRUD ---
def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    
    # Update booking paid_amount
    booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
    if booking:
        booking.paid_amount += payment.amount
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_booking_payments(db: Session, booking_id: int):
    return db.query(models.Payment).filter(models.Payment.booking_id == booking_id).all()
