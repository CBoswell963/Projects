import json
import os
import signal
import unittest
import requests
from cops_platform.container_runtime.tests.safety_test_util import SafeTestCase
from dotenv import load_dotenv
load_dotenv()


class ContainerRuntimeTestCase(SafeTestCase):
    """
    Unit tests for the Container Runtime.
    IMPORTANT: Currently exceptions are thrown when running this as coverage report with the nose module.
    However, the coverage report should still be logged. This is to due with how the tearDownClass method
    is sending a signal to kill the Container Runtime, so that it can gracefully shut down and clean up
    all its containers and threads. There is likely a better way to handle this but we did have not have time
    to fix given the duration of this project.
    """
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        from cops_platform.container_runtime.app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        # Sends a SIGINT signal to the currently running process
        os.kill(os.getpid(), signal.SIGINT)

    def test_invalid_user(self):
        """
        Tests a service request with invalid user credentials
        """
        with self.app.app_context():

            data = {"username": 'does_not_exist', "service": 'course_manager'}
            response = self.client.post("http://127.0.0.1:5000/service_request", data=data)
            res = json.loads(response.data)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(res['message'], "Given credentials are not valid")

    def test_invalid_service(self):
        """
        Tests a service request with an invalid service name
        """
        with self.app.app_context():
            data = {"username": 'student', "service": 'does_not_exist'}
            response = self.client.post("http://127.0.0.1:5000/service_request", data=data)

            res = json.loads(response.data)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(res['message'], "This is not a valid service")

    def test_service_request(self):
        """
        Tests valid service requests for the Container Runtime
        NOTE: In order for this to pass the user with the username "student" must exist in the PostgreSQL DB.
        """
        with self.app.app_context():

            # Tests that a valid service request returns a 200 status code
            data = {"username": 'student', "service": 'course_manager'}
            response = self.client.post("http://127.0.0.1:5000/service_request", data=data)
            res = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
           
            self.assertEqual(res['message'], "Service request was successful")
            url = res['url']

            # Retrieve the session cookie from the response
            auth_cookie = None
            for cookie in self.client.cookie_jar:
                if cookie.name == 'session':
                    auth_cookie = {'session': cookie.value}
                    break

            # Assert the user can connect to the running service in the container
            response = requests.get(url, cookies=auth_cookie)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), "Logged in as student")

            # Assert the health check thread is working
            auth_cookie = {'session': response.cookies.get('session')}
            response = requests.get(url + "/api/health_check")
            self.assertEqual(json.loads(response.content), "Success")

            # Assert the health check thread will return "Unsuccessful" message after the user logs out
            response = requests.get(url + "/api/logout", cookies=auth_cookie)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), "Successfully logged out")

            response = requests.get(url + "/api/health_check")
            self.assertEqual(json.loads(response.content), "Unsuccessful")

