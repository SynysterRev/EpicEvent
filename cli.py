import click

import sentry_sdk


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
from init_db import init_db

if __name__ == "__main__":
    cli()
