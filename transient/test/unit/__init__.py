import unittest
from mixer.backend.sqlalchemy import Mixer
from transient.lib.database import session, init_db


class BaseTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(BaseTestCase, self).__init__(methodName)
        self.mixer = Mixer(session=session, commit=True)
        self.session = session
        init_db()
