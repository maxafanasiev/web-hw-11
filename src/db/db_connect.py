import configparser

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

config = configparser.ConfigParser()
config.read('src/config/config.ini')

user = config.get('DB', 'user')
password = config.get('DB', 'pass')
db_name = config.get('DB', 'db_name')
domain = config.get('DB', 'domain')
port = config.get('DB', 'port')

# connect to cluster on AtlasDB with connection string

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db_name}")


def get_db():
    db = Session(engine)
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()
