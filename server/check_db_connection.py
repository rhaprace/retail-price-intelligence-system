"""
Simple script to check database connection.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")
else:
    load_dotenv()  # Try default .env location
    if Path('.env').exists():
        print("Loaded .env file from current directory")
    else:
        print("No .env file found, using environment variables or defaults")


def check_connection():
    """Check database connection."""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME', 'retail_price_intelligence')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    password_display = '*' * len(password) if password else '(empty)'
    print(f"Password: {password_display}")
    
    if not password:
        print("\n WARNING: Password is empty!")
        print("   Make sure DB_PASSWORD is set in your .env file")
        print("   Example: DB_PASSWORD=your_password")
    print()
    
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\n Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n No tables found. Run the schema:")
                print("   psql -U postgres -d retail_price_intelligence -f database/schema.sql")
            
            return True
            
    except OperationalError as e:
        print("Connection failed!")
        error_msg = str(e)
        print(f"Error: {error_msg}")
        
        if "does not exist" in error_msg:
            print("\n💡 Database doesn't exist. Create it:")
            print(f"   createdb -U postgres {database}")
        elif "password authentication failed" in error_msg:
            print("\n💡 Wrong password. Check your DB_PASSWORD in .env")
        elif "could not connect" in error_msg:
            print("\n💡 Cannot connect to server. Check:")
            print("   1. PostgreSQL service is running")
            print("   2. Host and port are correct")
            print("   3. Firewall allows connections")
        else:
            print("\n💡 Check your database configuration in .env file")
        
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    check_connection()

