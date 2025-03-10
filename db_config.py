from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

db_url = (f"postgresql+psycopg2://{DB_HOSTNAME}:{DB_PASSWORD}@localhost:{DB_PORT}"
          f"/{DB_NAME}")

if db_url is None:
    raise ValueError("Environment variables must be set")

engine = create_engine(db_url, echo=True)