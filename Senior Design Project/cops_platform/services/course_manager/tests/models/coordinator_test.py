import unittest

from sqlalchemy.exc import IntegrityError

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Coordinator
import os


class CoordinatorTestCase(unittest.TestCase):
    """
    Unit tests for the Coordinator Model class.
    """
    def setUp(self):
        app_config = os.getenv('FLASK_CONFIG') or 'default'
        self.app = create_app(config_name=app_config)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        self.ctx.pop()

    def test_valid_coordinator0(self):
        # Create a valid coordinator and tests fields are set properly
        coordinator0 = Coordinator(username="coordinator_test_0", name="Coordinator Test 0")
        self.assertTrue(coordinator0.username is "coordinator_test_0")
        self.assertTrue(coordinator0.name is "Coordinator Test 0")

        # Add new coordinator to the database
        try:
            db.session.add(coordinator0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        coordinator0_db = Coordinator.query.filter_by(username=coordinator0.username).first()
        self.assertIsNotNone(coordinator0_db.id)
        self.assertTrue(coordinator0_db.username == "coordinator_test_0")
        self.assertTrue(coordinator0_db.name == "Coordinator Test 0")

    def test_valid_coordinator1(self):
        # Create a valid coordinator and tests fields are set properly
        # Name can be same but username has to be different
        coordinator1 = Coordinator(username="coordinator_test_1", name="Coordinator Test 0")
        self.assertTrue(coordinator1.username is "coordinator_test_1")
        self.assertTrue(coordinator1.name is "Coordinator Test 0")

        # Add new coordinator to the database
        try:
            db.session.add(coordinator1)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        coordinator1_db = Coordinator.query.filter_by(username=coordinator1.username).first()
        self.assertIsNotNone(coordinator1_db.id)
        self.assertTrue(coordinator1_db.username == "coordinator_test_1")
        self.assertTrue(coordinator1_db.name == "Coordinator Test 0")

    def test_invalid_coordinator(self):
        # Create a valid coordinator and tests fields are set properly
        coordinator0 = Coordinator(username="coordinator_test_0", name="Coordinator Test 0")
        self.assertTrue(coordinator0.username is "coordinator_test_0")
        self.assertTrue(coordinator0.name is "Coordinator Test 0")

        # Add new coordinator to the database
        try:
            db.session.add(coordinator0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Create a coordinator with the same username as added coordinator
        # Tests that Integrity error is thrown in Database
        coordinator2 = Coordinator(username="coordinator_test_0", name="Coordinator Test 2")
        try:
            db.session.add(coordinator2)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)
