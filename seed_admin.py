from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, crud

def seed_admin():
    db = SessionLocal()
    # Check if admin already exists
    admin = db.query(models.Admin).filter(models.Admin.email == "admin@anjalitent.com").first()
    if not admin:
        print("Creating default admin...")
        admin_in = models.Admin(
            name="Super Admin",
            email="admin@anjalitent.com",
            hashed_password=crud.get_password_hash("admin123")
        )
        db.add(admin_in)
        db.commit()
        print("Admin created: admin@anjalitent.com / admin123")
    else:
        print("Admin already exists. Updating password to admin123...")
        admin.hashed_password = crud.get_password_hash("admin123")
        db.commit()
    db.close()

if __name__ == "__main__":
    seed_admin()
