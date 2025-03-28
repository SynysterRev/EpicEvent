import click
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.client import Client
from models.collaborator import Collaborator
from models.contract import Contract, Status
from utils import util
from utils.permissions import login_required, permission, ActionType, ResourceType, \
    RoleType, check_filters
from views import view


@cli.command()
@click.option(
    "--status",
    type=click.Choice(["signed", "pending", "cancelled"]),
    default=None,
    help="Filter contracts by status (signed, pending, cancelled)",
)
@click.option(
    "--remaining-amount",
    is_flag=True,
    help="Display only contracts with remaining amount.",
)
@click.option(
    "--assigned",
    is_flag=True,
    help="Only return contracts assigned to current user",
)
@permission(ActionType.READ, ResourceType.CONTRACT)
@check_filters(ResourceType.CONTRACT, "status", "remaining_amount", "assigned")
@login_required(pass_token=True)
def get_contracts(token, status, remaining_amount, assigned):
    """Get all contracts"""
    with Session(engine) as session:
        select_stmt = select(Contract)
        if status:
            select_stmt = select_stmt.where(Contract.status == Status(status))
        if remaining_amount:
            select_stmt = select_stmt.where(Contract.remaining_amount > 0)
        if assigned:
            try:
                collaborator_id = token["id"]
            except KeyError:
                view.display_error(f"No id stocked in the current token.")
                return
            select_stmt = select_stmt.where(
                Contract.sales_contact_id == collaborator_id)
        contracts = session.execute(select_stmt).scalars().all()
        if not contracts:
            view.display_message(f"No contracts found.")
        for contract in contracts:
            view.display_message(contract)


@cli.command()
@permission(ActionType.CREATE, ResourceType.CONTRACT)
@login_required()
def create_contract():
    """Create a new contract"""
    with Session(engine) as session:
        client_id = util.ask_for_input("Client ID", util.validate_digit)
        client = session.get(Client, client_id)
        if not client:
            view.display_error(f"Client with id {client_id} does not exist.")
            return
        sales_contact_id = client.sales_contact_id
        collaborator = session.get(Collaborator, sales_contact_id)
        if not collaborator:
            view.display_error(f"Collaborator with id {sales_contact_id} does not "
                               f"exist. Check the client sales contact ID.")
            return
        if collaborator.role.name != RoleType.SALES:
            view.display_error(f"This collaborator cannot be assigned to a contract.")
            return

        total_amount = util.ask_for_input("Total amount ", util.validate_decimal)
        remaining_amount = util.ask_for_input("Total amount ", util.validate_decimal)
        status = util.choose_from_enum(Status)
        contract = Contract(total_amount, remaining_amount, status,
                            client_id, sales_contact_id)
        session.add(contract)
        session.commit()


@cli.command()
@permission(ActionType.UPDATE_ALL, ResourceType.CONTRACT)
@permission(ActionType.UPDATE_MINE, ResourceType.CONTRACT)
@login_required(pass_token=True)
def update_contract(token):
    """Update a contract"""
    with Session(engine) as session:
        contract_id = util.ask_for_input("Contract ID", util.validate_digit)
        contract = session.get(Contract, contract_id)
        if not contract:
            view.display_error(f"Contract with id {contract_id} does not exist.")
            return
        # if update mine check contract

        view.display_message(f"Updating {contract}")
        while True:
            choice = int(view.display_edit_contract())
            if 0 <= choice <= 6:
                if choice == 0:
                    break
                elif choice == 1:
                    contract.total_amount = util.ask_for_input("Total amount ",
                                                           util.validate_decimal)
                elif choice == 2:
                    contract.remaining_amount = util.ask_for_input("Remaining amount ",
                                                      util.validate_email)
                elif choice == 3:
                    contract.status = util.choose_from_enum(Status)
                elif choice == 4:
                    client_id = util.ask_for_input("Client ID ",
                                                    util.validate_digit)
                    if session.get(Client, client_id):
                        contract.client_id = client_id
                # do the client need to be changed too ?
                elif choice == 5:
                    sales_id = util.ask_for_input("Sales contact ID ",
                                                  util.validate_digit)
                    collaborator = session.get(Collaborator, sales_id)
                    if collaborator and collaborator.role.name == RoleType.SALES:
                        contract.sales_contact_id = sales_id
                    else:
                        view.display_error("Sales contact id does not exist.")
            else:
                view.display_error("Invalid choice.")
        session.commit()
        view.display_message(f"{contract} has been updated.", "green")



