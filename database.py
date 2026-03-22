from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://anjalitent_user:z9IkNJ8ZFH85dZ2SGXBDUO79BV1eyIw6@dpg-d6vsdjvfte5s73e2njqg-a/anjalitent" # Change 'postgres' and 'password' to your actual credentials
# If using PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
