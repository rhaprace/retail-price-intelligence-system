from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from models import SessionLocal


class DatabaseSession:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self) -> Session:
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {exc_val}")
        
        if exc_type in (HTTPException, RequestValidationError):
            return False
        
        if exc_type is not None:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal server error: {exc_val}")
        
        self.db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except (HTTPException, RequestValidationError):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        db.close()


def test_db_connection():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {"status": "connected", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": "Database connection failed", "error": str(e)}
    finally:
        db.close()

