import unittest
from sqlalchemy.exc import IntegrityError
import cops_platform
from cops_platform.services.course_manager.app import create_app, db
import cops_platform.services.course_manager.app.models
from datetime import time
import os


class MappingTestCase(unittest.TestCase):
    """
    Unit tests for the Course Student Mapping class.
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

    def test_invalid_mapping0(self):
        # Try to create a mapping between a course and a student
        # without a student, this should not be allowed

        # create a valid instructor and add them
        instructor = cops_platform.services.course_manager.app.models.Instructor(username="instructor",
                                                                                 name="Instructor")
        db.session.add(instructor)
        db.session.commit()

        # create a valid course and add it
        instructor = cops_platform.services.course_manager.app.models.Instructor.query.filter_by(
            username=instructor.username).first()
        start = time(12, 30)
        end = time(2, 15)
        course = cops_platform.services.course_manager.app.models.Course(name="CSC316", days="MW", start_time=start,
                                                                         end_time=end, instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        # create a mapping with a course, but no student then try to add it
        course = cops_platform.services.course_manager.app.models.Course.query.filter_by(name=course.name).first()
        mapping = cops_platform.services.course_manager.app.models.CourseStudentMapping(grade="4.0",
                                                                                        course_id=course.id,
                                                                                        student_id=None)
        # check to see if mapping properly failed
        try:
            db.session.add(mapping)
            db.session.commit()
            self.fail()
        except IntegrityError as err:
            self.assertIsNotNone(err)
