import click
import sentry_sdk
from sqlalchemy import select
from sqlalchemy.orm import Session

import utils.permissions
import validator
from cli import cli
from db_config import engine
from models.collaborator import Collaborator
from models.contract import Contract, Status
from models.event import Event
from utils import util
from utils.permissions import PermissionManager
from utils.permissions import (
    login_required,
    permission,
    ActionType,
    ResourceType,
    RoleType,
)
from views import view


@cli.command()
@click.option(
    "--assign",
    type=click.Choice(["all", "assigned", "no-contact"]),
    default="all",
    help="Return all the events with or without filter",
)
@permission(ActionType.READ, resource=ResourceType.EVENT)
@login_required(pass_token=True)
def get_events(token, assign):
    """Get all events

    Args:
        token (str): The token of the current user.
        assign (str, optional): Filter events based on assignment.
            - "all": Returns all events.
            - "assigned": Returns events assigned to the current user.
            - "no-contact": Returns events without a support contact.
            Defaults to "all".
            This is enabled by using the --assign flag.
    """
    with Session(engine) as session:
        stmt = select(Event)
        try:
            collaborator_id = token["id"]
        except KeyError:
            view.display_error(
                f"No id stocked in the current token. Try to login again."
            )
            return
        if assign == "assigned":
            stmt = stmt.where(Event.support_contact_id == collaborator_id)
        elif assign == "no-contact":
            stmt = stmt.where(Event.support_contact_id == None)
        all_events = session.execute(stmt).scalars().all()
        if not all_events:
            view.display_message(f"No events found.")
        for event in all_events:
            view.display_message(event)


@cli.command()
@permission(ActionType.CREATE, resource=ResourceType.EVENT)
@login_required(pass_token=True)
def create_event(token):
    """Create a new event"""
    with Session(engine) as session:
        contract_id = util.ask_for_input("Contract ID", validator.validate_digit)
        contract = session.get(Contract, contract_id)
        if not contract:
            view.display_error(f"Contract with id {contract_id} does not exist.")
            return
        try:
            token_id = token["id"]
        except KeyError:
            view.display_error(f"No id stocked in the current token. Try to log again.")
            return

        if token_id != contract.sales_contact_id:
            view.display_error(
                "You are not authorized to create events for this contract."
            )
            return

        if contract.status != Status.SIGNED:
            view.display_error("The contract must be signed in order to create events.")
            return

        start_date = util.ask_for_input(
            "Start date (yyyy-mm-dd)", validator.validate_date
        )
        start_time = util.ask_for_input("Start time (HH:MM)", validator.validate_time)

        end_date = util.ask_for_input("End date (yyyy-mm-dd)", validator.validate_date)
        end_time = util.ask_for_input("End time (HH:MM)", validator.validate_time)

        location = util.ask_for_input("Location")
        attendees = util.ask_for_input("Attendees", validator.validate_digit)
        support_id = util.ask_for_input("Support ID (optional)")
        if not support_id.isdigit():
            support_id = None
        if support_id:
            collaborator = session.get(Collaborator, support_id)
            if not collaborator:
                view.display_error(
                    f"Collaborator with id {support_id} does not " f"exist."
                )
                return
            if collaborator.role.name != RoleType.SUPPORT:
                view.display_error(f"This collaborator cannot be assigned to a event.")
                return
        event = Event(
            start_date,
            start_time,
            end_date,
            end_time,
            location,
            attendees,
            contract_id,
            support_id,
        )
        session.add(event)
        session.commit()


@cli.command()
@permission(ActionType.UPDATE_ALL, ActionType.UPDATE_MINE, resource=ResourceType.EVENT)
@login_required(pass_token=True)
def update_event(token):
    """Update an event"""
    with Session(engine) as session:
        event_id = util.ask_for_input("Event ID", validator.validate_digit)
        event = session.get(Event, event_id)
        if not event:
            view.display_error(f"Event with id {event_id} does not exist.")
            return
        is_manager = PermissionManager.has_permission(
            RoleType(token["role"]), ActionType.UPDATE_ALL, resource=ResourceType.EVENT
        )
        if not is_manager:
            if event.support_contact_id != token["id"]:
                view.display_error(
                    "You are not authorized to update an event to which you are not assigned."
                )
                return
        max_choice = 8 if is_manager else 6
        view.display_message(f"Updating\n{event}", "blue")
        while True:
            choice = int(view.display_edit_event(is_manager))
            if 0 <= choice <= max_choice:
                if choice == 0:
                    break
                elif choice == 1:
                    event.start_date = util.ask_for_input(
                        "Start date", validator.validate_date
                    )
                elif choice == 2:
                    event.start_time = util.ask_for_input(
                        "Start time", validator.validate_time
                    )
                elif choice == 3:
                    event.end_date = util.ask_for_input(
                        "End date", validator.validate_date
                    )
                elif choice == 4:
                    event.end_time = util.ask_for_input(
                        "End time", validator.validate_date
                    )
                elif choice == 5:
                    event.location = util.ask_for_input("Location")
                elif choice == 6:
                    event.attendees = util.ask_for_input(
                        "Attendees", validator.validate_digit
                    )
                elif choice == 7:
                    contract_id = util.ask_for_input(
                        "Contract ID ", validator.validate_digit
                    )
                    if session.get(Contract, contract_id):
                        event.contract_id = contract_id
                    else:
                        view.display_error(
                            f"Contract with id {contract_id} does not exist."
                        )
                elif choice == 8:
                    collaborator_id = util.ask_for_input(
                        "Support ID ", validator.validate_digit
                    )
                    collaborator = session.get(Collaborator, collaborator_id)
                    if collaborator and collaborator.role.name == RoleType.SUPPORT:
                        event.support_contact_id = collaborator_id
                    else:
                        view.display_error("Support contact id does not exist.")
            else:
                view.display_error("Invalid choice.")
        session.commit()
        view.display_message(f"{event} has been updated.", "green")
