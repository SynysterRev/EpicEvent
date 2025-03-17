from getpass import getpass

import click
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.collaborator import Collaborator, Role
from models.client import Client
from models.event import Event
from models.contract import Contract
from utils import util
from utils.permissions import RoleType, ActionType, ResourceType


def choose_from_enum(enum_class, prompt="Choose an option"):
    options = {str(i + 1): member for i, member in enumerate(enum_class)}
    print(f"{prompt}:")
    for num, member in options.items():
        print(f"{num}. {member.name}")

    while True:
        choice = input("Enter the number of your choice: ").strip()
        if choice in options:
            return options[choice]
        print("Invalid choice. Please enter a valid number.")


def get_id_from_enum_role(enum_class, role):
    with Session(engine) as session:
        role_id = session.execute(
            select(Role.id).where(Role.name == role)
        ).scalar()
        if not role_id:
            print(f"Error: Role {role.value} not found in collaborator_role!")
            return
        return role_id


@cli.command()
def create_collaborator():
    """Create a new collaborator"""
    collaborator_email = input("Enter the collaborator email: ")
    with Session(engine) as session:
        collaborator = session.execute(select(Collaborator).where(Collaborator.email ==
                                                                  collaborator_email)).scalar()
        if collaborator:
            click.echo("This email already exists.")
            return
        collaborator_password = getpass("Enter the collaborator password: ")
        collaborator_name = input("Enter the collaborator name: ")
        collaborator_first_name = input("Enter the collaborator first name: ")
        collaborator_phone_number = input("Enter the collaborator phone number: ")
        role = choose_from_enum(RoleType)
        role_id = get_id_from_enum_role(RoleType, role)
        hashed_password = util.hash_password(collaborator_password)
        collaborator = Collaborator(collaborator_email, collaborator_password,
                                    collaborator_name, collaborator_first_name,
                                    collaborator_phone_number,
                                    role_id)
        session.add(collaborator)
        session.commit()


@cli.command()
def login():
    """Log the user in."""
    with Session(engine) as session:
        collaborator_login = input("Please enter your login: ")
        collaborator = session.execute(select(Collaborator).where(Collaborator.email ==
                                                                  collaborator_login)).scalar()
        if collaborator:
            try:
                collaborator_password = getpass("Please enter your password: ")
                util.verify_password(collaborator_password, collaborator.password)
                click.echo("Login successful.")
            except VerifyMismatchError as e:
                click.echo("Incorrect password.")
                return
            # token = util.create_token(collaborator)
            print(collaborator.has_permission(ActionType.DELETE,
                                              ResourceType.EVENT))
        else:
            click.echo("This email is not registered.")
