import click
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.contract import Contract, Status
from utils.permissions import login_required, permission, ActionType, ResourceType
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
    help="Filter contracts by remaining amount",
)
@click.option(
    "--assigned",
    is_flag=True,
    help="Only return contracts assigned to current user",
)
@permission(ActionType.READ, ResourceType.CONTRACT)
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
