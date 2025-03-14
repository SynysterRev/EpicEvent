from sqlalchemy.orm import Session

from db_config import engine

def main():

    try:
        with engine.connect() as connection:
            print("Connection established")
    except Exception as ex:
        print(ex)

    with Session(engine) as session:
        try:
            session.add('SELECT 1')
            print("ca marche")
        except Exception as ex:
            print(ex)
        finally:
            session.close()

if __name__ == '__main__':
    main()