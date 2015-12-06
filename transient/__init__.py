from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


def setup():
    from transient.lib.database import init_db
    init_db()


def teardown():
    from transient.lib.database import session
    session.remove()
