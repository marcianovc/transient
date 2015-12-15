from flask.ext.testing import TestCase
from transient.lib.database import session


class BaseIntegrationTest(TestCase):

    def create_app(self):
        from transient.api import app
        return app

    def setUp(self):
        super(BaseIntegrationTest, self).setUp()
        self.session = session

    def tearDown(self):
        super(BaseIntegrationTest, self).tearDown()
        self.session.remove()
