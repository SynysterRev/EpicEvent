from getpass import getpass

import psycopg2
from sqlalchemy import create_engine, insert, select

from db_config import DB_NAME, DB_PORT
from models import Base
from models.collaborator import Role
from utils.permissions import RoleType


def init_db():
    print("You must use a user with the permission to create tables (postgres by "
          "default).")
    db_user = (input("Enter user name(default 'postgres') : ") or "postgres")
    db_password = getpass("Enter the password for this user : ")

    db_url = (f"postgresql+psycopg2://{db_user}:{db_password}@localhost:{DB_PORT}"
              f"/{DB_NAME}")
    try:
        conn = psycopg2.connect(
            dbname="postgres", user=db_user, password=db_password, host="localhost",
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # create database only if it doesn't exist.
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' successfully created.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()

        try:
            engine = create_engine(db_url)
            Base.metadata.create_all(engine)
            print(f"The tables have been successfully created in the database "
                  f"'{DB_NAME}'.")
            with engine.connect() as conn:
                result = conn.execute(select(Role)).fetchone()

                if result is None:
                    conn.execute(insert(Role),
                                 [
                                     {"name": RoleType.MANAGEMENT},
                                     {"name": RoleType.SALES},
                                     {"name": RoleType.SUPPORT},
                                 ], )
                    conn.commit()
                print("RoleType tables populated.")
        except Exception as e:
            print(f"Error when trying to create tables : {e}")


    except Exception as e:
        print("An error occured :", e)


if __name__ == "__main__":
    init_db()
