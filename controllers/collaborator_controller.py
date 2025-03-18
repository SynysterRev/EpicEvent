from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli import cli
from db_config import engine
from models.collaborator import Collaborator, Role
from models.client import Client
from models.event import Event
from models.contract import Contract
from utils import util
from utils.permissions import RoleType, login_required, ActionType, ResourceType
from views import view


def choose_from_enum(enum_class, prompt="Choose an option"):
    options = {str(i + 1): member for i, member in enumerate(enum_class)}
    view.display_message(f"{prompt}:")
    for num, member in options.items():
        view.display_message(f"{num}. {member.name}")

    while True:
        choice = view.get_input("Enter the number of your choice").strip()
        if choice in options:
            return options[choice]
        view.display_error("Invalid choice. Please enter a valid number.")


def get_id_from_enum_role(role, session):
    role_id = session.execute(
        select(Role.id).where(Role.name == role)
    ).scalar()
    if not role_id:
        view.display_error(f"Role {role.value} not found in collaborator_role.")
        return None
    return role_id


@cli.command()
@login_required
def create_collaborator():
    """Create a new collaborator"""
    with Session(engine) as session:
        is_valid = False
        while not is_valid:
            collaborator_email = util.ask_for_input("Enter the collaborator email",
                                                    util.validate_email)
            collaborator = session.execute(
                select(Collaborator).where(Collaborator.email ==
                                           collaborator_email)).scalar()
            if collaborator:
                view.display_error("This email already exists.")
            else:
                is_valid = True

        collaborator_password = util.ask_for_password("Enter the collaborator "
                                                      "password: ",
                                                      util.validate_password)
        collaborator_name = util.ask_for_input("Enter the collaborator name: ",
                                               util.validate_name)
        collaborator_first_name = util.ask_for_input("Enter the collaborator first "
                                                     "name: ", util.validate_name)
        collaborator_phone_number = util.ask_for_input("Enter the collaborator phone "
                                                       "number: ",
                                                       util.validate_phone_number)
        role = choose_from_enum(RoleType)
        role_id = get_id_from_enum_role(role, session)
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
        collaborator_login = util.ask_for_input("Please enter your email")
        collaborator = session.execute(select(Collaborator).where(Collaborator.email ==
                                                                  collaborator_login)).scalar()
        if collaborator:
            try:
                collaborator_password = util.ask_for_password("Please enter your password")
                util.verify_password(collaborator_password, collaborator.password)
            except VerifyMismatchError as e:
                view.display_error("Incorrect password.")
                return
            try:
                util.create_token(collaborator)
                view.display_message("Login successful.", 'green')
            except Exception as e:
                view.display_error(str(e))
        else:
            view.display_error("This email is not registered.")
