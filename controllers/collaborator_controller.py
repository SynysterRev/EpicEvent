from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

import validator
from cli import cli
from db_config import engine
from models.collaborator import Collaborator, Role
from utils import util
from utils.permissions import (
    RoleType,
    login_required,
    ActionType,
    ResourceType,
    permission,
)
from views import view


def get_id_from_enum_role(role, session):
    role_id = session.execute(select(Role.id).where(Role.name == role)).scalar()
    if not role_id:
        view.display_error(f"Role {role.value} not found in collaborator_role.")
        return None
    return role_id


@cli.command()
@permission(ActionType.CREATE, resource=ResourceType.COLLABORATOR)
@login_required()
def create_collaborator():
    """Create a new collaborator"""
    with Session(engine) as session:
        collaborator_email = util.ask_for_input(
            "Enter the collaborator email", validator.validate_email
        )
        collaborator_phone_number = util.ask_for_input(
            "Enter the collaborator phone number ", validator.validate_phone_number
        )
        collaborator = session.execute(
            select(Collaborator).where(
                or_(
                    Collaborator.email == collaborator_email,
                    Collaborator.phone_number == collaborator_phone_number,
                )
            )
        ).scalar_one_or_none()
        if collaborator:
            view.display_error("This email or phone number already exists.")
            return

        collaborator_password = util.ask_for_password(
            "Enter the collaborator password ", validator.validate_password
        )
        collaborator_name = util.ask_for_input(
            "Enter the collaborator last_name ", validator.validate_name
        )
        collaborator_first_name = util.ask_for_input(
            "Enter the collaborator first name ", validator.validate_name
        )

        role = util.choose_from_enum(RoleType)
        role_id = get_id_from_enum_role(role, session)
        collaborator = Collaborator(
            collaborator_email,
            collaborator_password,
            collaborator_first_name,
            collaborator_name,
            collaborator_phone_number,
            role_id,
        )
        session.add(collaborator)
        session.commit()


def ask_collaborator_id(session):
    email_phone = util.ask_for_input(
        "Enter the collaborator email or phone number "
    )
    collaborator = session.execute(
        select(Collaborator).where(
            or_(
                Collaborator.email == email_phone,
                Collaborator.phone_number == email_phone,
            )
        )
    ).scalar_one_or_none()

    return collaborator


@cli.command()
@permission(ActionType.UPDATE_ALL, resource=ResourceType.COLLABORATOR)
@login_required()
def update_collaborator():
    """Update collaborator"""
    with Session(engine) as session:
        collaborator = ask_collaborator_id(session)

        if collaborator is None:
            view.display_error("No collaborator found.")
            return

        view.display_message(f"Updating\n{collaborator}", "blue")
        while True:
            choice = int(view.display_edit_collaborator())
            if 0 <= choice <= 6:
                if choice == 0:
                    break
                elif choice == 1:
                    collaborator.first_name = util.ask_for_input("First name ",
                                                                 validator.validate_name)
                elif choice == 2:
                    collaborator.name = util.ask_for_input("Last name ",
                                                           validator.validate_name)
                elif choice == 3:
                    collaborator.email = util.ask_for_input("Email ",
                                                            validator.validate_email)
                elif choice == 4:
                    collaborator.password = util.hash_password(util.ask_for_password(
                        "Password ", validator.validate_password))
                elif choice == 5:
                    collaborator.phone_number = util.ask_for_input("Phone number ",
                                                                   validator.validate_phone_number)
                elif choice == 6:
                    role = util.choose_from_enum(RoleType)
                    role_id = get_id_from_enum_role(role, session)
                    collaborator.role_id = role_id
            else:
                view.display_error("Invalid choice.")
        session.commit()
        view.display_message(f"{collaborator} has been updated.", "green")


@cli.command()
@permission(ActionType.DELETE, resource=ResourceType.COLLABORATOR)
@login_required(pass_token=True)
def delete_collaborator(token):
    """Delete collaborator"""
    with Session(engine) as session:
        collaborator = ask_collaborator_id(session)

        if collaborator is None:
            view.display_error("No collaborator found.")
            return

        choice = util.ask_for_input(
            f"Are you sure you want to delete {collaborator} ? Y/N").lower()
        if choice in ("y", "yes"):
            session.delete(collaborator)
            session.commit()
            if collaborator.id == token["id"]:
                logout_user()


@cli.command()
def login():
    """Log the user in."""
    with Session(engine) as session:
        collaborator_login = util.ask_for_input("Please enter your email")
        collaborator = session.execute(
            select(Collaborator).where(Collaborator.email == collaborator_login)
        ).scalar_one_or_none()
        if collaborator:
            try:
                collaborator_password = util.ask_for_password(
                    "Please enter your password"
                )
                util.verify_password(collaborator_password, collaborator.password)
            except VerifyMismatchError:
                view.display_error("Incorrect password.")
                return
            try:
                util.create_token(collaborator)
                view.display_message("Login successful.", "green")
            except Exception as e:
                view.display_error(str(e))
        else:
            view.display_error("This email is not registered.")


@cli.command()
def logout():
    """Log the user out."""
    logout_user()

def logout_user():
    util.delete_token()
    view.display_message("Logout successful.", "green")
