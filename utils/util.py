import os
import re
from datetime import UTC
from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from jwt import ExpiredSignatureError

from db_config import SECRET_KEY, TOKEN, reload_env
from views import view

DEFAULT_TOKEN_EXPIRY_MINUTES = 30


def hash_password(password):
    ph = PasswordHasher()
    return ph.hash(password)


def verify_password(plain_password, hashed_password):
    ph = PasswordHasher()
    return ph.verify(hashed_password, plain_password)


def ask_for_input(message, validate_function=None):
    if validate_function is None:
        return view.get_input(message)
    is_valid = False
    value = ""
    while not is_valid:
        value = view.get_input(message)
        try:
            is_valid = validate_function(value)
        except ValueError as e:
            view.display_error(str(e))
    return value


def ask_for_password(message, validate_function=None):
    if validate_function is None:
        return view.get_password(message)
    is_valid = False
    value = ""
    while not is_valid:
        value = view.get_password(message)
        try:
            is_valid = validate_function(value)
        except ValueError as e:
            view.display_error(str(e))
    return value


def get_token():
    if not TOKEN or not SECRET_KEY:
        raise ValueError("TOKEN or SECRET_KEY not found in environment variables. "
                         "Try to log again")
    try:
        token = TOKEN
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token expired. Please log in again.")
    except Exception as e:
        raise ValueError(f"Failed to decode token: {str(e)}")


def create_token(collaborator):
    secret_key = SECRET_KEY
    if secret_key is None:
        raise ValueError(
            "SECRET_KEY not found in environment variables. Use the init command first.")
    payload = {
        "id": collaborator.id,
        "first_name": collaborator.first_name,
        "name": collaborator.name,
        "role": collaborator.role.name.value,
        "exp": datetime.now(UTC) + timedelta(minutes=DEFAULT_TOKEN_EXPIRY_MINUTES),
    }
    token = jwt.encode(payload=payload, key=secret_key)
    write_env_variable("TOKEN", token)
    return token

def delete_token():
    secret_key = SECRET_KEY
    if secret_key is None:
        raise ValueError(
            "SECRET_KEY not found in environment variables. Use the init command first.")
    write_env_variable("TOKEN", "")

def write_env_variable(var_name, var_value):
    env_file = '.env'
    try:
        if os.path.exists(env_file):
            with open(env_file, 'r') as env:
                lines = env.readlines()
        else:
            lines = []

        updated = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{var_name}="):
                new_lines.append(f"{var_name}='{var_value}'\n")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"{var_name}='{var_value}'\n")

        with open(env_file, 'w') as env:
            env.writelines(new_lines)
            reload_env()
    except PermissionError:
        raise PermissionError(f"Permission denied: Unable to access '{env_file}' file.")
    except Exception as e:
        raise Exception(f"Error writing to '{env_file}': {str(e)}")


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