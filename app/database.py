import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Configuration ---
# The DDL uses SQLite-specific syntax, so we'll configure for SQLite.
# You can easily swap this out for PostgreSQL, MySQL, etc.
# Example for PostgreSQL: "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///../artifacts/database.db")

# Create the SQLAlchemy engine
# connect_args is needed only for SQLite to allow multi-threaded access.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
# Each instance of a SessionLocal class will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# All our ORM models will inherit from this class.
Base = declarative_base()


# --- FastAPI Dependency ---
def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    
    This function is a generator that yields a session and ensures it is
    always closed, even if an error occurs during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()