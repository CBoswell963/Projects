import unittest
import json

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.tests.db.generate_db import main as reset_database
from cops_platform.services.course_manager.app.models import Student, Course, Instructor, CourseStudentMapping
from datetime import time


class UserControllerTestCase(unittest.TestCase):
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

    def test_user_login_and_view_account(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        #  Accessing account information before logging in returns 401 response
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "401 UNAUTHORIZED")

        # Logging in successfully returns 200 code with message
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(json.loads(response.data), "Successfully logged in")

        # User can view their account information after logging in
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "200 OK")
        user = json.loads(response.data)

        self.assertEqual(user['username'], 'coordinator')
        self.assertEqual(user['name'], 'Coordinator')
        self.assertIsNotNone(user['id'])

        # Logging out successfully returns 200 code with message
        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(json.loads(response.data), "Successfully logged out")

        #  Accessing account information after logging out returns 401 response
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "401 UNAUTHORIZED")

    def test_add_new_user(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid user returns a 200 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="student"))
        self.assertEqual(response.status, "200 OK")

        # Creating a user with the same username returns a 400 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="student"))
        self.assertEqual(response.status, "400 BAD REQUEST")

        # Creating a user with an incorrect role returns a 400 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="role"))
        self.assertEqual(response.status, "400 BAD REQUEST")

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_delete_user(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('coordinator')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='coordinator'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Creating valid user returns a 200 status
        response = self.client.post('/api/user', data=dict(username='student_test', name='Student Tester',
                                                           role="student"))
        self.assertEqual(response.status, "200 OK")

        # Sending invalid role with the DELETE request returns a 404 status code
        response = self.client.delete('/api/user', data=dict(username='student_test', role='error'))
        self.assertEqual(response.status_code, 400)

        # DELETE request for a student that exists returns a 200 status code
        response = self.client.delete('/api/user', data=dict(username='student_test', role='student'))
        self.assertEqual(response.status, "200 OK")

        # DELETE request for the previously deleted student returns a 404 status code
        response = self.client.delete('/api/user', data=dict(username='student_test', role='student'))
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

    def test_student_view_gpa(self):
        # Initializes app for testing with coordinator role
        self.setUpCustom('student')

        # Logging in to account
        response = self.client.post('/api/login', data=dict(username='student'), follow_redirects=True)
        self.assertEqual(response.status, "200 OK")

        # Enroll student in courses and view grades
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

        student = Student.query.filter_by(username='student').first()
        course = Course.query.filter_by(name="CSC326").first()
        mapping1 = CourseStudentMapping(grade="2.0", course_id=course.id, student_id=student.id)
        db.session.add(mapping1)
        db.session.commit()

        student = Student.query.filter_by(username='student').first()
        course = Course.query.filter_by(name="CSC331").first()
        mapping1 = CourseStudentMapping(course_id=course.id, student_id=student.id)
        db.session.add(mapping1)
        db.session.commit()

        # User can view their account information after logging in
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "200 OK")
        user = json.loads(response.data)

        self.assertEqual(user['username'], 'student')
        self.assertEqual(user['name'], 'Student')
        self.assertIsNotNone(user['id'])
        self.assertEqual(user['gpa'], 3.0)

        # DELETE request for a course that exists returns a 200 status code
        response = self.client.delete('/api/course', data=dict(course_name="CSC316"))
        self.assertEqual(response.status, "200 OK")

        # User can view their account information after logging in
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "200 OK")
        user = json.loads(response.data)

        self.assertEqual(user['username'], 'student')
        self.assertEqual(user['name'], 'Student')
        self.assertIsNotNone(user['id'])
        self.assertEqual(user['gpa'], 2.0)

        # DELETE request for a course that exists returns a 200 status code
        response = self.client.delete('/api/course', data=dict(course_name="CSC326"))
        self.assertEqual(response.status, "200 OK")

        # User can view their account information after logging in
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "200 OK")
        user = json.loads(response.data)

        self.assertEqual(user['username'], 'student')
        self.assertEqual(user['name'], 'Student')
        self.assertIsNotNone(user['id'])
        self.assertEqual(user['gpa'], 0.0)

        # DELETE request for a course that exists returns a 200 status code
        response = self.client.delete('/api/course', data=dict(course_name="CSC331"))
        self.assertEqual(response.status, "200 OK")

        # User can view their account information after logging in
        response = self.client.get('/api/user')
        self.assertEqual(response.status, "200 OK")
        user = json.loads(response.data)

        self.assertEqual(user['username'], 'student')
        self.assertEqual(user['name'], 'Student')
        self.assertIsNotNone(user['id'])
        self.assertEqual(user['gpa'], 0.0)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
