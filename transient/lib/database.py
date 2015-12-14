import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from transient import settings


def get_connection_string():
    """
    Return a postgres connection string using config in env variables.
    """
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    database = settings.POSTGRES_DATABASE
    username = settings.POSTGRES_USERNAME
    password = settings.POSTGRES_PASSWORD

    if not (database and username):
        sys.exit("Missing database configuration")

    if password:
        auth = "%s:%s@" % (username, password)
    else:
        auth = "%s@" % (username)

    return "postgresql://%s%s:%s/%s" % (auth, host, port, database)


engine = create_engine(get_connection_string())
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()
