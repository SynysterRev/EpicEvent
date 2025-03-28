import click
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.event import Event
from utils.permissions import login_required, permission, ActionType, ResourceType
from views import view


@cli.command()
@click.option(
    "--assign",
    type=click.Choice(["all, assigned, no-contact"]),
    default="all",
    help="Return all the events with or without filter",
)
@permission(ActionType.READ, ResourceType.EVENT)
@login_required(pass_token=True)
def get_events(token, assign):
    """Get all events"""
    with Session(engine) as session:
        stmt = select(Event)
        try:
            collaborator_id = token["id"]
        except KeyError:
            view.display_error(
                f"No id stocked in the current token. Try to login again.")
            return
        if assign == "assigned":
            stmt = stmt.where(Event.sales_contact_id==collaborator_id)
        elif assign == "no-contact":
            stmt = stmt.where(Event.sales_contact_id==None)
        all_events = session.execute(stmt)
        if not all_events:
            view.display_message(f"No events found.")
        for event in all_events:
            view.display_message(event)
