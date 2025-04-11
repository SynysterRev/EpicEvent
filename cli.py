import os

import click

import sentry_sdk
from dotenv import load_dotenv

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
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
from init_db import init_db

if __name__ == "__main__":
    cli()
