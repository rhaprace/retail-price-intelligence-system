"""
Database setup script.
Creates the database and runs the schema.
"""
import os
import sys
import subprocess
from pathlib import Path


def check_postgresql():
    """Check if PostgreSQL is installed and accessible."""
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("PostgreSQL not found in PATH")
        print("   Please install PostgreSQL or add it to your PATH")
        return False


def check_database_exists(db_name):
    """Check if database exists."""
    try:
        result = subprocess.run(
            ['psql', '-lqt'],
            capture_output=True,
            text=True,
            env=os.environ
        )
        databases = [line.split('|')[0].strip() for line in result.stdout.split('\n')]
        return db_name in databases
    except:
        return False


def create_database(db_name, db_user=None):
    """Create the database."""
    print(f"\n Creating database '{db_name}'...")
    try:
        cmd = ['createdb', db_name]
        if db_user:
            cmd.extend(['-U', db_user])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Database '{db_name}' created successfully")
            return True
        else:
            if 'already exists' in result.stderr.lower():
                print(f"Database '{db_name}' already exists")
                return True
            else:
                print(f"Error creating database: {result.stderr}")
                if 'role' in result.stderr.lower() and 'does not exist' in result.stderr.lower():
                    print("\n💡 Tip: Try using the 'postgres' superuser:")
                    print(f"   createdb -U postgres {db_name}")
                return False
    except FileNotFoundError:
        print("'createdb' command not found")
        print("   Please make sure PostgreSQL is installed and in your PATH")
        return False


def run_schema(db_name, schema_file, db_user=None):
    """Run the schema SQL file."""
    print(f"\n Running schema from '{schema_file}'...")
    
    if not Path(schema_file).exists():
        print(f"Schema file not found: {schema_file}")
        return False
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cmd = ['psql', '-d', db_name, '-f', schema_file]
        if db_user:
            cmd.extend(['-U', db_user])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Schema applied successfully")
            return True
        else:
            print(f"Error running schema:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("Database Setup for Retail Price Intelligence System")
    print("=" * 60)
    
    # Get database name and user from env or use defaults
    db_name = os.getenv('DB_NAME', 'retail_price_intelligence')
    db_user = os.getenv('DB_USER', 'postgres')  # Default to postgres superuser
    schema_file = Path(__file__).parent / 'database' / 'schema.sql'
    
    print(f"\nDatabase name: {db_name}")
    print(f"Database user: {db_user}")
    print(f"Schema file: {schema_file}")
    
    # Check PostgreSQL
    if not check_postgresql():
        print("\nSetup failed: PostgreSQL not found")
        print("\nPlease install PostgreSQL:")
        print("  Windows: https://www.postgresql.org/download/windows/")
        print("  Mac: brew install postgresql")
        print("  Linux: sudo apt-get install postgresql")
        sys.exit(1)
    
    # Try to create database with postgres user first
    print(f"\nAttempting to create database using user '{db_user}'...")
    if not create_database(db_name, db_user):
        print(f"\nFailed with user '{db_user}'. Trying 'postgres' superuser...")
        db_user = 'postgres'
        if not create_database(db_name, db_user):
            print("\n❌ Could not create database.")
            print("\nOptions:")
            print("1. Use postgres superuser manually:")
            print(f"   createdb -U postgres {db_name}")
            print(f"   psql -U postgres -d {db_name} -f database/schema.sql")
            print("\n2. Create a PostgreSQL user:")
            print("   psql -U postgres")
            print("   CREATE USER your_username WITH PASSWORD 'your_password';")
            print("   ALTER USER your_username CREATEDB;")
            sys.exit(1)
    
    # Run schema
    if not run_schema(db_name, str(schema_file), db_user):
        print("\n❌ Setup failed: Could not apply schema")
        print(f"\nTry running manually:")
        print(f"   psql -U {db_user} -d {db_name} -f database/schema.sql")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
    print(f"\nDatabase: {db_name}")
    print(f"User: {db_user}")
    print("\nYou can now:")
    print("  1. Start the API: python run_api.py")
    print("  2. Run tests: python test_api.py")
    print("  3. Add sources: python scrapers/setup_source.py")
    
    # Update .env file if it doesn't exist
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print(f"\n💡 Tip: Create a .env file with:")
        print(f"   DB_USER={db_user}")
        print(f"   DB_NAME={db_name}")


if __name__ == "__main__":
    main()

