import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN = os.getenv("TOKEN")

db_url = (f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}"
          f"/{DB_NAME}")

if db_url is None:
    raise ValueError("Environment variables must be set")

engine = create_engine(db_url, echo=False)


def reload_env():
    """Reload environment variables from .env file and update global variables."""
    global DB_USER, DB_PASSWORD, DB_PORT, DB_NAME, SECRET_KEY, TOKEN
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "epic_events")
    SECRET_KEY = os.getenv("SECRET_KEY")
    TOKEN = os.getenv("TOKEN")
