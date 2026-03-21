# Anjali Tent Backend (FastAPI)

This is the backend API for the Anjali Tent & Caterers platform. It allows the owner to:
- Manage Bookings
- Keep track of Inventory (Tents, Chairs, etc.)
- Track Rentals (Who rented what, and if it's returned)
- View Contact Us Inquiries from clients

## Setup Instructions

1. **Open a terminal in this folder** (`c:\anjalitent\backend`)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation
Once the server is running, explore the automatic interactive API documentation:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Redoc:** http://127.0.0.1:8000/redoc

## Endpoints
- `POST /users/` - Create a new user/client
- `POST /inventory/` - Add new items to inventory
- `POST /bookings/` - Book an event for a user
- `POST /rentals/` - Rent an inventory item for a booking
- `PUT /rentals/{id}/return` - Mark a rented item as returned (restores stock)
- `POST /inquiries/` - Submit a contact form
- `PUT /inquiries/{id}/resolve` - Mark an inquiry as resolved
