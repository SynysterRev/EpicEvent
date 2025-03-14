from getpass import getpass
import click
import secrets

@click.group()
def cli():
    pass

@cli.command()
def init():
    """
    Create .env files with needed information
    Generate secret key for JWT Token
    Create database and tables
    """
    click.echo("Creating .env file...")
    db_hostname = input("Database hostname: ")
    db_password = getpass("Database password: ")
    db_port = input("Database port (5432 by default, left empty to use it) : ") or 5432
    db_name = input("Database name : ")
    secret_key = secrets.token_hex(32)
    try:
        with open('.env', 'w') as env:
            env.write(f"DB_HOSTNAME='{db_hostname}'\n")
            env.write(f"DB_PASSWORD='{db_password}'\n")
            env.write(f"DB_PORT='{db_port}'\n")
            env.write(f"DB_NAME='{db_name}'\n")
            env.write(f"SECRET_KEY='{secret_key}'")
            click.echo("File '.env' created.")
    except PermissionError:
        click.echo(f"Permission denied: Unable to create '.env' file.")
        return
    click.echo("Initializing database...")
    from init_db import init_db
    init_db()


if __name__ == '__main__':
    cli()