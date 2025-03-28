import click


def get_input(message):
    value = click.prompt(message)
    return value


def get_password(message):
    password = click.prompt(message, hide_input=True)
    return password


def display_error(message):
    click.secho(message, fg='red')


def display_message(message, color=None):
    click.secho(message, fg=color)


def display_edit_collaborator():
    choice = click.prompt(
        "1. Edit first name\n"
        "2. Edit last name\n"
        "3. Edit email\n"
        "4. Edit password\n"
        "5. Edit phone number\n"
        "6. Edit role\n"
        "0. Quit\n")
    return choice


def display_edit_client():
    choice = click.prompt(
        "1. Edit full name\n"
        "2. Edit email\n"
        "3. Edit phone number\n"
        "4. Edit company\n"
        "5. Edit sales contact\n"
        "0. Quit\n")
    return choice


def display_edit_contract():
    choice = click.prompt(
        "1. Edit total amount\n"
        "2. Edit remaining amount\n"
        "3. Edit status\n"
        "4. Edit client_id\n"
        "5. Edit sales contact id\n"
        "0. Quit\n")
    return choice
