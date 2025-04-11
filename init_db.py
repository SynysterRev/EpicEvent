import secrets

import psycopg2
import sentry_sdk

import views.view
from db_config import DB_NAME, engine, DB_USER, DB_PASSWORD, DB_PORT
from models import Base
from cli import cli
from utils.util import write_env_variable


@cli.command()
def init():
    """
    Generate secret key for JWT Token
    Create database and tables
    """
    views.view.display_message("Registering init command")

    secret_key = secrets.token_hex(32)

    try:
        views.view.display_message("Writing in .env file...")
        write_env_variable("SECRET_KEY", secret_key)
        views.view.display_message("Secret key generated.", "green")
    except PermissionError as e:
        views.view.display_error(f"Permission denied: Unable to write in '.env' file.")
        sentry_sdk.capture_exception(e)
        return
    views.view.display_message("Initializing database...")
    init_db()

def init_db():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host="localhost",
            port=DB_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # create database only if it doesn't exist.
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            views.view.display_message(f"Database '{DB_NAME}' successfully created.", "green")
        else:
            views.view.display_message(f"Database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()

        try:
            Base.metadata.create_all(engine)
            views.view.display_message(
                f"The tables have been successfully created in the database "
                f"'{DB_NAME}'.", "green"
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            views.view.display_error(e)

    except Exception as e:
        sentry_sdk.capture_exception(e)
        views.view.display_error(e)


if __name__ == "__main__":
    init_db()
