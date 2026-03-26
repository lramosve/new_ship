from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Specify the correct database URL with default settings
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/app_db'

# Attempt to create an engine and connect to the database
engine = create_engine(DATABASE_URL)

try:
    # Connect to the database and execute a trivial command
    with engine.connect() as connection:
        from sqlalchemy import text
        result = connection.execute(text("SELECT 1"))
        print("Connection successful, result:", result.scalar())
except OperationalError as e:
    print("Connection failed:", str(e))