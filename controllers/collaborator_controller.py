from getpass import getpass

import jwt
from cryptography.hazmat.primitives import serialization
from jwt import ExpiredSignatureError

from models.collaborator import Collaborator
from utils import cli, utils
import click
from db_config import SECRET_KEY

class CollaboratorController:
    pass


@cli.command()
def login():
    # collaborator_login = input("Please enter your login: ")
    # collaborator_password = getpass("Please enter your password: ")
    # get password from db
    # utils.verify_password(collaborator_password)

    #encode token
    payload = {
        # "first_name": collaborator_login,
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY)

    # decode token
    try:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoicG90YXRvIiwiYmFzZSI6MzJ9.WGwuB_F-Mwn5nr5ymuOfcSlxnyDipgDN2RuJCB37SG0"
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        print("ExpiredSignatureError")

