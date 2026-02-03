
import os
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus

# The connection string I used for Azure
# postgresql://astroadmin:A1!StrongPass123@astrology-db-central-7387.postgres.database.azure.com:5432/postgres

user = "astroadmin"
password = quote_plus("A1!StrongPass123")
host = "astrology-db-central-7387.postgres.database.azure.com"
dbname = "postgres"

# Try with and without sslmode=require
urls = [
    f"postgresql://{user}:{password}@{host}:5432/{dbname}",
    f"postgresql://{user}:{password}@{host}:5432/{dbname}?sslmode=require"
]

for url in urls:
    print(f"\n--- Testing URL: {url.replace(password, '****')} ---")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print("Successfully connected to the database!")
            
            # Check for tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Existing tables: {tables}")
            
            if 'users' not in tables:
                print("Table 'users' NOT FOUND. Attempting to initialize schema...")
                # We can't easily import the models here without setup, 
                # but we can see if it's missing.
            else:
                print("Table 'users' exists.")
                # Check for any rows
                result = conn.execute(text("SELECT count(*) FROM users")).scalar()
                print(f"Number of users: {result}")
                
    except Exception as e:
        print(f"Connection failed: {e}")
