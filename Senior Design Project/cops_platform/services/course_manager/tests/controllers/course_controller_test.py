import unittest
from datetime import time

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Student, Course, Instructor, CourseStudentMapping
from cops_platform.services.course_manager.tests.db.generate_db import main as reset_database


class CourseControllerTestCase(unittest.TestCase):
    """
    Unit tests for the User Controller class.
    """

    def setUpCustom(self, role):
        reset_database()
        self.app = create_app(config_name='default', role=role)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_add_new_course(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid course returns a 200 status
        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test', days='M',
                                                             start_time="12:00", end_time="01:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        response = self.client.post('/api/course', data=dict(name='course_test', days='M',
                                                             start_time="12:00", end_time="01:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status_code, 400)

        # Creating a new course with an incorrect instructor returns a 400 status
        response = self.client.post('/api/course', data=dict(name='course_test', day='M',
                                                             start_time="8:00", end_time="12:00",
                                                             instructor="Course Instructor"))
        self.assertEqual(response.status, "400 BAD REQUEST")

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_delete_course(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid course returns a 200 status
        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test', days='M',
                                                             start_time="12:00", end_time="01:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        course = Course.query.filter_by(name="course_test").first()

        # DELETE request for course that does not exist returns 400 status
        response = self.client.delete('/api/course', data=dict(course_name="does_not_exist"))
        self.assertEqual(response.status_code, 400)

        # DELETE request for a course that exists returns a 200 status code
        response = self.client.delete('/api/course', data=dict(course_name=course.name))
        self.assertEqual(response.status, "200 OK")

        # DELETE request for the previously deleted course returns a 400 status code
        response = self.client.delete('/api/course', data=dict(course_name="course_test"))
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_enroll_student(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid user returns a 200 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="student"))
        self.assertEqual(response.status, "200 OK")

        # Creating valid course returns a 200 status
        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test', days='M',
                                                             start_time="12:00", end_time="13:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        student = Student.query.filter_by(username="student_test").first()
        course = Course.query.filter_by(name="course_test", days="M", instructor_id=instructor.id).first()

        # Creating a valid mapping returns a 200 status
        response = self.client.post('/api/mapping', data=dict(username=student.username, course_name=course.name))

        self.assertEqual(response.status, "200 OK")

        response = self.client.post('/api/mapping', data=dict(username=student.username, course_name=course.name))

        self.assertEqual(response.status_code, 400)
        db.session.rollback()
        mapping = CourseStudentMapping.query.filter_by(course_id=course.id, student_id=student.id).first()
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.student_id, student.id)
        self.assertEqual(mapping.course_id, course.id)
        self.assertIsNone(mapping.grade)

        # DELETE request for a course that exists returns a 200 status code
        response = self.client.delete('/api/course', data=dict(course_name=course.name))
        self.assertEqual(response.status, "200 OK")

        mapping = CourseStudentMapping.query.filter_by(course_id=course.id, student_id=student.id).first()

        self.assertIsNone(mapping)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_edit_course_grade(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid user returns a 200 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="student"))
        self.assertEqual(response.status, "200 OK")

        # Creating valid course returns a 200 status
        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test', days='M',
                                                             start_time="12:00", end_time="13:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        student = Student.query.filter_by(username="student_test").first()
        course = Course.query.filter_by(name="course_test", days="M", instructor_id=instructor.id).first()

        # Creating a valid mapping returns a 200 status
        response = self.client.post('/api/mapping', data=dict(username=student.username, course_name='course_test'))
        self.assertEqual(response.status, "200 OK")

        mapping = CourseStudentMapping.query.filter_by(course_id=course.id, student_id=student.id).first()
        self.assertIsNone(mapping.grade)

        response = self.client.put('/api/mapping/grade', data=dict(username=student.username,
                                                                   course_name=course.name, grade=3.5))
        self.assertEqual(response.status, "200 OK")

        mapping = CourseStudentMapping.query.filter_by(course_id=course.id, student_id=student.id).first()

        self.assertEqual(mapping.grade, 3.5)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_course_schedule_student(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('student')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='student'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test1', days='M',
                                                             start_time="12:00", end_time="01:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        course = Course.query.filter_by(name='course_test1').first()

        response = self.client.post('/api/mapping', data=dict(course_name=course.name, username='student'))

        self.assertEqual(response.status, "200 OK")

        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test2', days='W',
                                                             start_time="8:00", end_time="9:00",
                                                             instructor_username=instructor.username))

        self.assertEqual(response.status, "200 OK")

        course = Course.query.filter_by(name='course_test2').first()

        response = self.client.post('/api/mapping', data=dict(course_name=course.name, username='student'))

        self.assertEqual(response.status, "200 OK")

        instructor = Instructor.query.filter_by(username="instructor").first()
        response = self.client.post('/api/course', data=dict(name='course_test3', days='W',
                                                             start_time="11:00", end_time="1:00",
                                                             instructor_username=instructor.username))
        self.assertEqual(response.status, "200 OK")

        course = Course.query.filter_by(name='course_test3').first()

        response = self.client.post('/api/mapping', data=dict(course_name=course.name, username='student'))

        self.assertEqual(response.status, "200 OK")

        response = self.client.get('/api/schedule')

        self.assertEqual(response.status, "200 OK")

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_course_schedule_instructor(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('instructor')

        instructor = Instructor.query.filter_by(username='instructor').first()
        start = time(9, 30)
        end = time(11, 15)
        course = Course(name="CSC326", days="MW", start_time=start, end_time=end, instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        start = time(2, 30)
        end = time(4, 15)
        course = Course(name="CSC331", days="TH", start_time=start, end_time=end, instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        student1 = Student(username="spencer", name="Spencer Yoder")
        db.session.add(student1)
        db.session.commit()

        student1 = Student.query.filter_by(username=student1.username).first()
        course1 = Course.query.filter_by(name="CSC326").first()
        mapping1 = CourseStudentMapping(grade="4.0", course_id=course1.id, student_id=student1.id)
        db.session.add(mapping1)
        db.session.commit()

        course2 = Course.query.filter_by(name="CSC331").first()
        mapping2 = CourseStudentMapping(grade="4.0", course_id=course2.id, student_id=student1.id)
        db.session.add(mapping2)
        db.session.commit()

        course3 = Course.query.filter_by(name="CSC316").first()
        mapping3 = CourseStudentMapping(grade="4.0", course_id=course3.id, student_id=student1.id)
        db.session.add(mapping3)
        db.session.commit()

        student2 = Student(username="caleb", name="Caleb Boswell")
        db.session.add(student2)
        db.session.commit()

        student2 = Student.query.filter_by(username=student2.username).first()
        mapping4 = CourseStudentMapping(grade="4.0", course_id=course1.id, student_id=student2.id)
        db.session.add(mapping4)
        db.session.commit()

        mapping5 = CourseStudentMapping(grade="4.0", course_id=course2.id, student_id=student2.id)
        db.session.add(mapping5)
        db.session.commit()

        student3 = Student(username="jeen", name="Jeen Shaji")
        db.session.add(student3)
        db.session.commit()

        student3 = Student.query.filter_by(username=student3.username).first()
        mapping6 = CourseStudentMapping(grade="4.0", course_id=course1.id, student_id=student3.id)
        db.session.add(mapping6)
        db.session.commit()

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='instructor'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        response = self.client.get('/api/schedule')

        self.assertEqual(response.status, "200 OK")

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_delete_instructor(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        instructor = Instructor.query.filter_by(username='instructor').first()
        start = time(9, 30)
        end = time(11, 15)
        course = Course(name="CSC326", days="MW", start_time=start, end_time=end, instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        start = time(2, 30)
        end = time(4, 15)
        course = Course(name="CSC331", days="TH", start_time=start, end_time=end, instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        student1 = Student(username="spencer", name="Spencer Yoder")
        db.session.add(student1)
        db.session.commit()

        student1 = Student.query.filter_by(username=student1.username).first()
        course1 = Course.query.filter_by(name="CSC326").first()
        mapping1 = CourseStudentMapping(grade="4.0", course_id=course1.id, student_id=student1.id)
        db.session.add(mapping1)
        db.session.commit()

        course2 = Course.query.filter_by(name="CSC331").first()
        mapping2 = CourseStudentMapping(grade="4.0", course_id=course2.id, student_id=student1.id)
        db.session.add(mapping2)
        db.session.commit()

        course3 = Course.query.filter_by(name="CSC316").first()
        mapping3 = CourseStudentMapping(grade="4.0", course_id=course3.id, student_id=student1.id)
        db.session.add(mapping3)
        db.session.commit()

        mapping = CourseStudentMapping.query.filter_by(course_id=course1.id).first()
        self.assertIsNotNone(mapping)

        mapping = CourseStudentMapping.query.filter_by(course_id=course2.id).first()
        self.assertIsNotNone(mapping)

        mapping = CourseStudentMapping.query.filter_by(course_id=course3.id).first()
        self.assertIsNotNone(mapping)

        db.session.delete(instructor)
        db.session.commit()

        course_del = Course.query.filter_by(name="CSC331").first()
        self.assertIsNone(course_del)

        course_del = Course.query.filter_by(name="CSC326").first()
        self.assertIsNone(course_del)

        course_del = Course.query.filter_by(name="CSC316").first()
        self.assertIsNone(course_del)

        mapping = CourseStudentMapping.query.filter_by(course_id=course1.id).first()
        self.assertIsNone(mapping)

        mapping = CourseStudentMapping.query.filter_by(course_id=course2.id).first()
        self.assertIsNone(mapping)

        mapping = CourseStudentMapping.query.filter_by(course_id=course3.id).first()
        self.assertIsNone(mapping)
