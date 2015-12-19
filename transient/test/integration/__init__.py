from flask.ext.testing import TestCase
from transient.lib.database import session
from transient.models.payment import Payment
from transient.models.transaction import Transaction


class BaseIntegrationTest(TestCase):

    def create_app(self):
        from transient.api import app
        return app

    def setUp(self):
        pass

    def tearDown(self):
        Transaction.query.delete()
        Payment.query.delete()
        session.commit()
        session.remove()
