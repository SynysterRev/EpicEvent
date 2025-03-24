import click
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.client import Client
from utils import util
from utils.permissions import login_required, ActionType, ResourceType, permission
from views import view


@cli.command()
@click.option(
    "--assigned",
    is_flag=True,
    help="Only return clients assigned to current user",
)
@permission(ActionType.READ, ResourceType.CLIENT)
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
            stmt = stmt.where(Client.id == collaborator_id)
        all_clients = session.execute(stmt)
        if not all_clients:
            view.display_message(f"No clients found.")
        for client in all_clients:
            view.display_message(client)


@cli.command()
@permission(ActionType.CREATE, ResourceType.CLIENT)
@login_required(pass_token=True)
def create_client(token):
    """Create a new client"""
    with Session(engine) as session:
        client_name = util.ask_for_input("Enter your client full name",
                                         util.validate_name)
        client_email = util.ask_for_input("Enter your client email",
                                          util.validate_email)
        client_phone = util.ask_for_input("Enter your client phone number",
                                          util.validate_phone_number)
        client_company = util.ask_for_input("Enter your client company")
        sales_id = token["id"]
        client = Client(client_name, client_email, client_phone, client_company,
                        sales_contact_id=sales_id)
        try:
            session.add(client)
            session.commit()
            view.display_message("Client created successfully.", "green")
        except IntegrityError as e:
            view.display_error(str(e))

# @cli.command()
# @login_required
# def update_client():
#     """Update a client"""
#     with Session(engine) as session:
#         is_valid = False
#         while not is_valid:
#             client_email = util.ask_for_input("Enter your client email",
#                                               util.validate_email)
#             client = session.execute(
#                 select(Client).where(Client.email ==
#                                            client_email)).scalar()
#             if not client:
#                 view.display_error("This email does not exist.")
#             else:
#                 is_valid = True
#
#         update_stmt = update(Client).where(Client.email == client_email).values(
#             full_name="")
