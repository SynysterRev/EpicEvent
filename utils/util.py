import os
import secrets
from datetime import datetime, timedelta
from datetime import UTC

import jwt
from argon2 import PasswordHasher
from jwt import ExpiredSignatureError

from db_config import SECRET_KEY, TOKEN, reload_env

DEFAULT_TOKEN_EXPIRY_MINUTES = 30


def hash_password(password):
    ph = PasswordHasher()
    return ph.hash(password)


def verify_password(plain_password, hashed_password):
    ph = PasswordHasher()
    return ph.verify(hashed_password, plain_password)


def get_token():
    if not TOKEN or not SECRET_KEY:
        raise ValueError("TOKEN or SECRET_KEY not found in environment variables.")
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
        raise ValueError("SECRET_KEY not found in environment variables. Use the init command first.")
    payload = {
        "first_name": collaborator.first_name,
        "name": collaborator.name,
        "role": collaborator.role.name.name,
        "exp": datetime.now(UTC) + timedelta(DEFAULT_TOKEN_EXPIRY_MINUTES),
    }
    token = jwt.encode(payload=payload, key=secret_key)
    write_env_variable("TOKEN", token)
    return token


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
