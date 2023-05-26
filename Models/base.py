from sqlalchemy.orm import declarative_base

from newmain import session

Model       = declarative_base()
Model.query = session.query_property()
