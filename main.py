from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import engine, get_db
import cloudinary
import cloudinary.utils
import time
import os

# Cloudinary Configuration (should ideally be in .env)
# For now using the values we know from frontend
CLOUDINARY_CLOUD_NAME = "dwohs6fpq"
CLOUDINARY_API_KEY = "388713291888126"
CLOUDINARY_API_SECRET = "M2I_39-0W_K8D2m8Y1m8_j8_G8" # Example secret

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Anjali Tent Backend API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Anjali Tent API is running"}

# --- Admins ---
@app.post("/admins/", response_model=schemas.AdminDisplay)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    if crud.get_admin_by_email(db, email=admin.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_admin(db=db, admin=admin)

# --- Clients ---
@app.post("/clients/", response_model=schemas.ClientDisplay)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    if crud.get_client_by_email(db, email=client.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_client(db=db, client=client)

@app.get("/clients/", response_model=List[schemas.ClientDisplay])
def read_clients(db: Session = Depends(get_db)):
    return crud.get_clients(db)

# --- Login Endpoints ---
@app.post("/login/admin", response_model=schemas.AdminDisplay)
def login_admin(login_data: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = crud.verify_admin_login(db, login_data)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return admin

@app.post("/login/client", response_model=schemas.ClientDisplay)
def login_client(login_data: schemas.AdminLogin, db: Session = Depends(get_db)): # Reusing schema for convenience
    client = crud.verify_client_login(db, login_data.email, login_data.password)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return client

# --- Notifications ---
@app.post("/notifications/", response_model=schemas.NotificationDisplay)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    return crud.create_notification(db=db, notification=notification)

@app.get("/clients/{client_id}/notifications", response_model=List[schemas.NotificationDisplay])
def read_client_notifications(client_id: int, db: Session = Depends(get_db)):
    return crud.get_client_notifications(db=db, client_id=client_id)

# --- Inventory ---
@app.post("/inventory/", response_model=schemas.InventoryDisplay)
def create_inventory_item(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    return crud.create_inventory_item(db=db, item=item)

@app.get("/inventory/", response_model=List[schemas.InventoryDisplay])
def read_inventory(db: Session = Depends(get_db)):
    return crud.get_inventory(db)

@app.put("/inventory/{item_id}", response_model=schemas.InventoryDisplay)
def update_inventory_item(item_id: int, item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    db_item = crud.update_inventory_item(db=db, item_id=item_id, item_update=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/inventory/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_inventory_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# --- Bookings ---
@app.post("/bookings/", response_model=schemas.BookingDisplay)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    return crud.create_booking(db=db, booking=booking)

@app.get("/bookings/", response_model=List[schemas.BookingDisplay])
def read_bookings(db: Session = Depends(get_db)):
    return crud.get_bookings(db)

@app.get("/clients/{client_id}/bookings", response_model=List[schemas.BookingDisplay])
def read_client_bookings(client_id: int, db: Session = Depends(get_db)):
    return crud.get_client_bookings(db=db, client_id=client_id)

@app.put("/bookings/{booking_id}", response_model=schemas.BookingDisplay)
def update_booking(booking_id: int, booking_update: schemas.BookingUpdate, db: Session = Depends(get_db)):
    db_booking = crud.update_booking(db=db, booking_id=booking_id, booking_update=booking_update)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check if status changed to confirmed to optionally send a notification
    if booking_update.status == "Confirmed":
        crud.create_notification(db, schemas.NotificationCreate(
            client_id=db_booking.client_id,
            message=f"Your booking for {db_booking.event_type} at {db_booking.venue} has been CONFIRMED by Admin."
        ))
        
    return db_booking

# --- Rentals ---
@app.post("/rentals/", response_model=schemas.RentalDisplay)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    db_rental = crud.create_rental(db=db, rental=rental)
    if not db_rental:
        raise HTTPException(status_code=400, detail="Not enough inventory available")
    return db_rental

@app.get("/rentals/", response_model=List[schemas.RentalDisplay])
def read_rentals(db: Session = Depends(get_db)):
    return crud.get_rentals(db)

@app.post("/bookings/{booking_id}/calculate-bill")
def trigger_bill_calculation(booking_id: int, db: Session = Depends(get_db)):
    total = crud.calculate_booking_bill(db, booking_id)
    return {"total_amount": total}

@app.put("/rentals/{rental_id}", response_model=schemas.RentalDisplay)
def update_rental_item(rental_id: int, rental_update: schemas.RentalUpdate, db: Session = Depends(get_db)):
    db_rental = crud.update_rental(db=db, rental_id=rental_id, rental_update=rental_update)
    if not db_rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental

# --- Inquiries / Contact Us ---
@app.post("/inquiries/", response_model=schemas.InquiryDisplay)
def create_inquiry(inquiry: schemas.InquiryCreate, db: Session = Depends(get_db)):
    return crud.create_inquiry(db=db, inquiry=inquiry)

@app.get("/inquiries/", response_model=List[schemas.InquiryDisplay])
def read_inquiries(db: Session = Depends(get_db)):
    return crud.get_inquiries(db)

@app.put("/inquiries/{inquiry_id}/resolve", response_model=schemas.InquiryDisplay)
def resolve_inquiry_status(inquiry_id: int, db: Session = Depends(get_db)):
    inquiry = crud.resolve_inquiry(db=db, inquiry_id=inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry

# --- Media ---
@app.get("/media/", response_model=List[schemas.MediaDisplay])
def read_all_media(db: Session = Depends(get_db)):
    return crud.get_all_media(db)

@app.post("/media/", response_model=schemas.MediaDisplay)
def create_media_item(media: schemas.MediaCreate, db: Session = Depends(get_db)):
    return crud.create_media(db=db, media=media)

@app.get("/media/", response_model=List[schemas.MediaDisplay])
def read_media(db: Session = Depends(get_db)):
    return crud.get_all_media(db)

@app.put("/media/{media_id}", response_model=schemas.MediaDisplay)
def update_media_item(media_id: int, media: schemas.MediaCreate, db: Session = Depends(get_db)):
    db_media = crud.update_media(db=db, media_id=media_id, media_update=media)
    if not db_media:
        raise HTTPException(status_code=404, detail="Media not found")
    return db_media

@app.delete("/media/{media_id}")
def delete_media_item(media_id: int, db: Session = Depends(get_db)):
    success = crud.delete_media(db=db, media_id=media_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"message": "Media deleted successfully"}

# --- Dashboard Stats ---
@app.get("/stats/")
def read_stats(db: Session = Depends(get_db)):
    bookings_count = len(crud.get_bookings(db))
    clients_count = len(crud.get_clients(db))
    inventory_count = len(crud.get_inventory(db))
    inquiries_count = len(crud.get_inquiries(db))
    # Simple recent activity (last 5 bookings)
    recent_bookings = crud.get_bookings(db)[-5:]
    recent_activity = [
        {"id": b.id, "type": "booking", "message": f"New booking: {b.event_type} at {b.venue}", "time": b.created_at}
        for b in recent_bookings
    ]
    
    return {
        "counts": {
            "bookings": bookings_count,
            "clients": clients_count,
            "inventory": inventory_count,
            "inquiries": inquiries_count
        },
        "recent_activity": recent_activity
    }

# --- Cloudinary Signed Upload ---
@app.get("/cloudinary-signature", response_model=schemas.CloudinarySignature)
def get_cloudinary_signature():
    timestamp = int(time.time())
    params = {
        "timestamp": timestamp,
    }
    signature = cloudinary.utils.api_sign_request(params, CLOUDINARY_API_SECRET)
    return {
        "signature": signature,
        "timestamp": timestamp,
        "api_key": CLOUDINARY_API_KEY,
        "cloud_name": CLOUDINARY_CLOUD_NAME
    }

# --- Payments ---
@app.post("/payments/", response_model=schemas.PaymentDisplay)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return crud.create_payment(db=db, payment=payment)

@app.get("/bookings/{booking_id}/payments", response_model=List[schemas.PaymentDisplay])
def read_booking_payments(booking_id: int, db: Session = Depends(get_db)):
    return crud.get_booking_payments(db=db, booking_id=booking_id)
