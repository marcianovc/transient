from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


def setup():
    from app.database import init_db
    init_db()


def teardown():
    from app.database import db_session
    db_session.remove()
