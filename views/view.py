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