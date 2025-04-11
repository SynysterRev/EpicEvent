import os
from datetime import date, time

import pytest
from click.testing import CliRunner
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from models.client import Client
from models.collaborator import Collaborator
from models.contract import Contract, Status
from models.event import Event
from utils.permissions import RoleType

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

db_url = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}"
    f"/epic_events_test"
)


@pytest.fixture(scope="function")
def test_db():
    """Crée une base de données de test avec PostgreSQL."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_db(test_db):
    """Nettoie la base de données avant chaque test."""
    connection = test_db.connect()
    transaction = connection.begin()

    # Supprime toutes les données des tables
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())

    transaction.commit()
    connection.close()


@pytest.fixture(scope="function")
def db_session(test_db):
    """Crée une nouvelle session de base de données pour chaque test."""
    connection = test_db.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session

    session.expunge_all()
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def management_user(db_session):
    """Crée un utilisateur avec le rôle management."""
    user = Collaborator(
        email="management@test.com",
        password="password123!",
        first_name="Management",
        name="User",
        phone_number="0123456789",
        role=RoleType.MANAGEMENT,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sales_user(db_session):
    """Crée un utilisateur avec le rôle sales."""
    user = Collaborator(
        email="sales@test.com",
        password="password123!",
        first_name="Sales",
        name="User",
        phone_number="0123456788",
        role=RoleType.SALES,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def support_user(db_session):
    """Crée un utilisateur avec le rôle support."""
    user = Collaborator(
        email="support@test.com",
        password="password123!",
        first_name="Support",
        name="User",
        phone_number="0123456787",
        role=RoleType.SUPPORT,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_client(db_session, sales_user):
    """Crée un client de test."""
    client = Client(
        full_name="Test Client",
        email="client@test.com",
        phone_number="0123456785",
        company="Test Company",
        sales_contact_id=sales_user.id,
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def test_contract(db_session, test_client, sales_user):
    """Crée un contrat de test."""
    contract = Contract(
        client_id=test_client.id,
        sales_contact_id=sales_user.id,
        total_amount=1000.0,
        remaining_amount=1000.0,
        status=Status.SIGNED,
    )
    db_session.add(contract)
    db_session.commit()
    return contract


@pytest.fixture
def test_event(db_session, test_contract, support_user):
    """Crée un événement de test."""
    event = Event(
        start_date=date(2024, 1, 1),
        start_time=time(9, 0),
        end_date=date(2024, 1, 1),
        end_time=time(17, 0),
        location="Test Location",
        attendees=10,
        contract_id=test_contract.id,
        support_contact_id=support_user.id,
    )
    db_session.add(event)
    db_session.commit()
    return event


@pytest.fixture
def mock_env_file():
    content = ["EXISTING_VAR='existing_value'\n", "ANOTHER_VAR='another_value'\n"]
    return content
