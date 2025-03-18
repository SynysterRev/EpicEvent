from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
import pytest
from sqlalchemy.orm import sessionmaker, declarative_base

# DB_NAME = "epic_event_test"
# DB_USER = "test_user"
# DB_PASSWORD = "<PASSWORD>"
#
#
# db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}"
#
# def db_prep():
#     print("dropping the old test db…")
#     engine = create_engine("postgresql://postgres@localhost/postgres")
#     conn = engine.connect()
#     try:
#         conn = conn.execution_options(autocommit=False)
#         conn.execute(f"DROP DATABASE {DB_NAME}")
#     except ProgrammingError:
#         print("Could not drop the database, probably does not exist.")
#     except OperationalError:
#         print(
#             "Could not drop database because it's being accessed by other users (psql prompt open?)")
#
#     print(f"test db dropped! about to create {DB_NAME}")
#     conn.execute(f"CREATE DATABASE {DB_NAME}")
#
#     try:
#         conn.execute(f"create user {DB_USER} with encrypted password "
#                      f"{DB_PASSWORD}")
#     except:
#         print("User already exists.")
#
#     conn.execute(
#         f"grant all privileges on database {DB_NAME} to {DB_USER}")
#
#     conn.close()
#     print("test db created")
#
#
# @pytest.fixture(scope="session", autouse=True)
# def fake_db():
#     db_prep()
#     print(f"initializing {DB_NAME}…")
#     from models.collaborator import Collaborator, Role
#     from models.event import Event
#     from models.contract import Contract
#     from models.client import Client
#     from models import Base
#
#     engine = create_engine(db_url)
#     Base.metadata.create_all(engine)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     db = SessionLocal()
#     print(f"{DB_NAME} ready to rock!")
#     try:
#         yield db
#     finally:
#         db.close()


@pytest.fixture(scope="session", autouse=True)
def mock_session():
    session = MagicMock()
    return session


@pytest.fixture
def mock_env_file():
    content = [
        "EXISTING_VAR='existing_value'\n",
        "ANOTHER_VAR='another_value'\n"
    ]
    return content