import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER", None)
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_NAME", None)

SECRET_KEY = os.getenv("SECRET_KEY", None)
TOKEN = os.getenv("TOKEN", None)

db_url = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
)

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
