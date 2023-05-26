from sqlalchemy.orm import declarative_base

from main import session

Model       = declarative_base()
Model.query = session.query_property()
