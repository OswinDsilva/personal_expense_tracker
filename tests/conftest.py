import pytest 
from backend.database import get_connection,release_connection
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute("TRUNCATE users,transactions,starting_balances,categories;")
        
        # Seeding categories 
        cur.execute("""INSERT INTO categories(name) VALUES ('Food'),('Transport'),('Entertainment'),('Academics'),('Clothing'),('Footwear');""")

        # Login using testclient 

    except Exception as e:
        connection.rollback()
        raise
    finally:
        release_connection(connection)