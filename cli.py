import os
from getpass import getpass
import click
import secrets

import sentry_sdk

import views.view
from db_config import DB_NAME, DB_PORT, DB_PASSWORD, DB_USER, SECRET_KEY


sentry_sdk.init(
    dsn="https://5b3f5cdfc81bac57dcca89423b862b67@o4509082863665152.ingest.de.sentry.io/4509082874675280",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


@click.group()
def cli():
    pass


from controllers import (
    collaborator_controller,
    client_controller,
    contract_controller,
    event_controller,
)


@click.command()
def init():
    """
    Create .env files with needed information
    Generate secret key for JWT Token
    Create database and tables
    """
    views.view.display_message("Registering init command")
    db_user = DB_USER
    if db_user == "":
        db_user = input("Database user: ")

    db_password = DB_PASSWORD
    if db_password == "":
        db_password = getpass("Database password: ")

    db_port = DB_PORT
    if db_port == "":
        db_port = input("Database port (5432 by default) : ") or 5432

    db_name = DB_NAME
    if db_name == "":
        db_name = input("Database name : ")

    secret_key = SECRET_KEY
    if not SECRET_KEY:
        secret_key = secrets.token_hex(32)

    try:
        views.view.display_message("Creating .env file...")
        with open(".env", "w") as env:
            env.write(f"DB_USER='{db_user}'\n")
            env.write(f"DB_PASSWORD='{db_password}'\n")
            env.write(f"DB_PORT='{db_port}'\n")
            env.write(f"DB_NAME='{db_name}'\n")
            env.write(f"SECRET_KEY='{secret_key}'\n")
            views.view.display_message("File '.env' created.")
    except PermissionError as e:
        views.view.display_error(f"Permission denied: Unable to create '.env' file.")
        sentry_sdk.capture_exception(e)
        return
    views.view.display_message("Initializing database...")
    from init_db import init_db

    init_db()


cli.add_command(init)

if __name__ == "__main__":
    cli()
