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
