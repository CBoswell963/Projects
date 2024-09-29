import unittest

from sqlalchemy.exc import IntegrityError

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Instructor
import os


class InstructorTestCase(unittest.TestCase):
    """
    Unit tests for the Instructor Model class.
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

    def test_valid_instructor0(self):
        # Create a valid instructor and tests fields are set properly
        instructor0 = Instructor(username="instructor_test_0", name="Instructor Test 0")
        self.assertTrue(instructor0.username is "instructor_test_0")
        self.assertTrue(instructor0.name is "Instructor Test 0")

        # Add new instructor to the database
        try:
            db.session.add(instructor0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        instructor0_db = Instructor.query.filter_by(username=instructor0.username).first()
        self.assertIsNotNone(instructor0_db.id)
        self.assertTrue(instructor0_db.username == "instructor_test_0")
        self.assertTrue(instructor0_db.name == "Instructor Test 0")

    def test_valid_instructor1(self):
        # Create a valid instructor and tests fields are set properly
        # Name can be same but username has to be different
        instructor1 = Instructor(username="instructor_test_1", name="Instructor Test 0")
        self.assertTrue(instructor1.username is "instructor_test_1")
        self.assertTrue(instructor1.name is "Instructor Test 0")

        # Add new instructor to the database
        try:
            db.session.add(instructor1)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        instructor1_db = Instructor.query.filter_by(username=instructor1.username).first()
        self.assertIsNotNone(instructor1_db.id)
        self.assertTrue(instructor1_db.username == "instructor_test_1")
        self.assertTrue(instructor1_db.name == "Instructor Test 0")

    def test_invalid_instructor(self):
        # Create a valid instructor and tests fields are set properly
        instructor0 = Instructor(username="instructor_test_0", name="Instructor Test 0")
        self.assertTrue(instructor0.username is "instructor_test_0")
        self.assertTrue(instructor0.name is "Instructor Test 0")

        # Add new instructor to the database
        try:
            db.session.add(instructor0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Create an instructor with the same username as added instructor
        # Tests that Integrity error is thrown in Database
        instructor2 = Instructor(username="instructor_test_0", name="Instructor Test 2")
        try:
            db.session.add(instructor2)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)
