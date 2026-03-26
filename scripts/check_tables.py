from sqlalchemy import create_engine, inspect

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/test_ship_db'
engine = create_engine(DATABASE_URL)

inspector = inspect(engine)
tables = inspector.get_table_names()

if not tables:
    print("No tables found in the database.")
else:
    print("Found tables:", tables)
