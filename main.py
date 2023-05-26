import os

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'teste.db'

engine = create_engine(f"sqlite:///{BASE_DIR}/{DB_NAME}", echo=False)

session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
    )
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def convertMaterial(materialFile):
    pass
