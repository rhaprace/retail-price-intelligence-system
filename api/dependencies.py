"""
Shared dependencies for API routes.
"""
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import traceback

from models import SessionLocal


def get_db():
    """Get database session with error handling."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = str(e)
        print(f"Database error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {error_msg}"
        )
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"Unexpected error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {error_msg}"
        )
    finally:
        db.close()


def test_db_connection():
    """Test database connection."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {"status": "connected", "message": "Database connection successful"}
    except Exception as e:
        error_msg = str(e)
        return {
            "status": "error",
            "message": "Database connection failed",
            "error": error_msg
        }
    finally:
        db.close()

