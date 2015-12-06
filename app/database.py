import sys
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def get_connection_string():
    """
    Return a postgres connection string using config in env variables.
    """
    host = environ.get("POSTGRES_HOST", "localhost")
    port = environ.get("POSTGRES_PORT", "5432")
    database = environ.get("POSTGRES_DATABASE")
    username = environ.get("POSTGRES_USERNAME")
    password = environ.get("POSTGRES_PASSWORD")

    if not (database and username and password):
        sys.exit("Missing database configuration")

    return "postgresql://%s:%s@%s:%s/%s" % (username, password, host,
        port, database)


engine = create_engine(get_connection_string())
db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)
