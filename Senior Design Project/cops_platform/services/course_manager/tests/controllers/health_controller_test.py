import unittest
import json

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.tests.db.generate_db import main as reset_database


class HealthCheckControllerTestCase(unittest.TestCase):
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

    def test_health_check_logout(self):

        self.setUpCustom('student')

        response = self.client.get('/api/health_check')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/login', data=dict(username='student'))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(json.loads(response.data), "Successfully logged in")

        response = self.client.get('/api/health_check')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/logout', follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(json.loads(response.data), "Successfully logged out")

        response = self.client.get('/api/health_check')
        self.assertEqual(response.status_code, 400)

