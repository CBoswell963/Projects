import unittest

from sqlalchemy.exc import IntegrityError

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Student
import os


class StudentTestCase(unittest.TestCase):
    """
    Unit tests for the Student Model class.
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

    def test_valid_student0(self):
        # Create a valid student and tests fields are set properly
        student0 = Student(username="student_test_0", name="Student Test 0")
        self.assertTrue(student0.username is "student_test_0")
        self.assertTrue(student0.name is "Student Test 0")

        # Add new student to the database
        try:
            db.session.add(student0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        student0_db = Student.query.filter_by(username=student0.username).first()
        self.assertIsNotNone(student0_db.id)
        self.assertTrue(student0_db.username == "student_test_0")
        self.assertTrue(student0_db.name == "Student Test 0")
        self.assertTrue(student0_db.gpa is None)

    def test_valid_student1(self):
        # Create a valid student with gpa value and tests fields are set properly
        student1 = Student(username="student_test_1", name="Student Test 1", gpa=3.0)
        self.assertTrue(student1.username is "student_test_1")
        self.assertTrue(student1.name is "Student Test 1")
        self.assertTrue(student1.gpa is 3.0)

        # Add new student to the database
        try:
            db.session.add(student1)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        student1_db = Student.query.filter_by(username=student1.username).first()
        self.assertIsNotNone(student1_db.id)
        self.assertTrue(student1_db.username == "student_test_1")
        self.assertTrue(student1_db.name == "Student Test 1")
        # self.assertTrue(student1_db.gpa is 3.0)

    def test_invalid_student(self):
        # Create a valid student and tests fields are set properly
        student0 = Student(username="student_test_0", name="Student Test 0")
        self.assertTrue(student0.username is "student_test_0")
        self.assertTrue(student0.name is "Student Test 0")

        # Add new student to the database
        try:
            db.session.add(student0)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Create a student with the same username as added student
        # Tests that Integrity error is thrown in Database
        student2 = Student(username="student_test_0", name="Student Test 2")
        try:
            db.session.add(student2)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)







