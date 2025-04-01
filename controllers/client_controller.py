import click
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import validator
from cli import cli
from db_config import engine
from models.client import Client
from models.collaborator import Collaborator
from utils import util
from utils.permissions import login_required, ActionType, ResourceType, permission, \
    RoleType, check_filters
from views import view


@cli.command()
@click.option(
    "--assigned",
    is_flag=True,
    help="Only return clients assigned to current user",
)
@permission(ActionType.READ, resource=ResourceType.CLIENT)
@check_filters(ResourceType.CLIENT, "assigned")
@login_required(pass_token=True)
def get_clients(token, assigned):
    """Get all clients"""
    with Session(engine) as session:
        stmt = select(Client)
        try:
            collaborator_id = token["id"]
        except KeyError:
            view.display_error(f"No id stocked in the current token. Try to log again.")
            return
        if assigned:
            stmt = stmt.where(Client.sales_contact_id == collaborator_id)
        all_clients = session.execute(stmt).scalars().all()
        if not all_clients:
            view.display_message(f"No clients found.")
        for client in all_clients:
            view.display_message(client)


@cli.command()
@permission(ActionType.CREATE, resource=ResourceType.CLIENT)
@login_required(pass_token=True)
def create_client(token):
    """Create a new client"""
    with Session(engine) as session:
        client_name = util.ask_for_input("Enter your client full name",
                                         validator.validate_name)
        client_email = util.ask_for_input("Enter your client email",
                                          validator.validate_email)
        client_phone = util.ask_for_input("Enter your client phone number",
                                          validator.validate_phone_number)
        client_company = util.ask_for_input("Enter your client company")
        try:
            token_id = token["id"]
        except KeyError:
            view.display_error(f"No id stocked in the current token. Try to log again.")
            return
        sales_id = token_id
        client = Client(client_name, client_email, client_phone, client_company,
                        sales_contact_id=sales_id)
        try:
            session.add(client)
            session.commit()
            view.display_message("Client created successfully.", "green")
        except IntegrityError as e:
            view.display_error(str(e))

def ask_client_id(session):
    email_phone = util.ask_for_input(
        "Enter the client email or phone number "
    )
    client = session.execute(
        select(Client).where(
            or_(
                Client.email == email_phone,
                Client.phone_number == email_phone,
            )
        )
    ).scalar_one_or_none()

    return client


@cli.command()
@permission(ActionType.UPDATE_MINE, resource=ResourceType.CLIENT)
@login_required(pass_token=True)
def update_client(token):
    """Update a client"""
    with Session(engine) as session:
        client = ask_client_id(session)
        if not client:
            view.display_error("No client found.")
            return
        try:
            token_id = token["id"]
        except KeyError:
            view.display_error(f"No id stocked in the current token. Try to log again.")
            return
        if client.id != token_id:
            view.display_error(f"This client is not assigned to you")
            return

        view.display_message(f"Updating\n{client}", "blue")
        while True:
            choice = int(view.display_edit_client())
            if 0 <= choice <= 6:
                if choice == 0:
                    break
                elif choice == 1:
                    client.first_name = util.ask_for_input("Full name ",
                                                                 validator.validate_name)
                elif choice == 2:
                    client.email = util.ask_for_input("Email ",
                                                            validator.validate_email)
                elif choice == 3:
                    client.phone_number = util.ask_for_input("Phone number ",
                                                                   validator.validate_phone_number)
                elif choice == 4:
                    client.company = util.ask_for_input("Company name ")
                elif choice == 5:
                    sales_id = util.ask_for_input("Sales contact id ",
                                                                 validator.validate_digit)
                    collaborator = session.get(Collaborator, sales_id)
                    if collaborator and collaborator.role.name == RoleType.SALES:
                        client.sales_contact_id = sales_id
                    else:
                        view.display_error("Sales contact id does not exist.")
            else:
                view.display_error("Invalid choice.")
        session.commit()
        view.display_message(f"{client} has been updated.", "green")