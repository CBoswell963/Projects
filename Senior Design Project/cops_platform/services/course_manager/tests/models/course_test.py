import unittest
from datetime import time

from sqlalchemy.exc import IntegrityError

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Course
from cops_platform.services.course_manager.app.models import Instructor
import os

class CourseTestCase(unittest.TestCase):
    """
    Unit tests for the Course Model class.
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

    def test_invalid_course0(self):
        # Try to add a course without time or instructor
        # This shouldn't be allowed
        course0 = Course(name="CSC 0", days="MW")
        try:
            db.session.add(course0)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)

    def test_invalid_course1(self):
        # Try to add a course without instructor
        start = time(9, 30)
        end = time(10, 45)
        course0 = Course(name="CSC 1", days="MW", start_time=start, end_time=end)
        try:
            db.session.add(course0)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)

    def test_valid_course2(self):
        # Create a valid instructor
        instructor0 = Instructor(username="instructor_test_0", name="Instructor Test 0")

        # Add new instructor to the database
        try:
            db.session.add(instructor0)
            db.session.commit()
        except Exception as e:
            self.fail()

        start = time(9, 30)
        end = time(10, 45)
        course2 = Course(name="CSC 2", days="MW", start_time=start, end_time=end, instructor_id=instructor0.id)
        self.assertTrue(course2.name is "CSC 2")
        self.assertTrue(course2.days is "MW")
        self.assertTrue(course2.start_time is start)
        self.assertTrue(course2.end_time is end)

        # Add new Course to the database
        try:
            db.session.add(course2)
            db.session.commit()
        except Exception as e:
            self.fail()

        # Test for equivalence in the Database object
        course2_db = Course.query.filter_by(name=course2.name).first()
        self.assertIsNotNone(course2_db.id)
        self.assertTrue(course2_db.name == "CSC 2")
        self.assertTrue(course2_db.days == "MW")
        self.assertTrue(course2_db.start_time == start)
        self.assertTrue(course2_db.end_time == end)
        self.assertTrue(course2_db.instructor_id == instructor0.id)






