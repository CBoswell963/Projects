"""
Course Manager App

The Flask app for running Course Manager. This contains all the required
configurations for initializing the app. The configs includes establishing a connection to the
database, setting the global role for this user, creating a randomized cookie
for this session for authentication, and registering the API endpoints for this app.

This file can also be imported as a module and contains the following
functions:
    * create_app - returns the app with all of the configurations set
    * get_role - returns the role of the user
"""
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from .extensions import api
from ..config import config
import os

# Global object for communicating with the database
db = SQLAlchemy()
# Global static value representing the user's ROLE (student, coordinator, or instructor)
ROLE = None
# Global static value representing logged in user's username
USERNAME = None


def create_app(config_name='default', role='student'):
    """
    Factory method for creating and returning a Flask app with all its required
    configurations and settings.

    Parameters
    ----------
    config_name: string
        The configuration settings to use for the app
    role : string
        The role for the user of this application (student, coordinator, or instructor)

    Returns
    -------
    app : Flask
        the Flask app with all initialized settings and values
    """

    # Initializes Flask app with the name of running python application
    app = Flask(__name__)

    # By default allows CORS for all domains on all routes
    # NOTE: In a real application would want to restrict this to specific addresses
    # "support_credentials=True" allows CORS to pass a session cookie for authentication
    CORS(app, supports_credentials=True)

    # Sets the configurations for this app based on the passed in config_name string value
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initializes the api object
    api.init_app(app)

    # Initializes the db object for this app
    db.init_app(app)

    # Sets the global role object to the passed in role parameter
    global ROLE
    ROLE = role

    # Initializes a randomized secret key for this session cookie
    app.secret_key = os.urandom(16)

    # Registers the api endpoints for this app
    __register_api(app)

    @app.before_request
    def before_request():
        """
        Automatically ends the session after the designated time of inactivity (default is 20 minutes).
        Sets the USERNAME to none if the user's session is no longer active.
        """
        # NOTE: If an unauthenticated request (i.e. a request sent without a session cookie)
        # is sent to a REST endpoint for course manager (other than the health_check endpoint or an OPTION method)
        # this will mark this USERNAME value as None. This means the next health check will fail
        # and shutdown the container running Course Manager. This is likely not behaviour you would
        # want in a real application because of the potential of Denial of Service attacks. However,
        # this is the best solution we could up for monitoring inactivity of the user with Flask
        # in our limited development time.
        # Ignoring any OPTIONS method due to this being called from the front-end when a PUT or DELETE request was sent.
        # This was causing issues since it doesn't have access to the session cookie and was causing the service to be
        # flagged as disconnected.
        if 'username' not in session and request.path != "/api/health_check" and request.method != "OPTIONS":
            global USERNAME
            USERNAME = None

    @app.after_request
    def after_request(res):
        """
        Session cookie time limit is refreshed every time a request is made by the user.
        This is used for tracking inactivity so it known that the user is still actively making requests
        to this service.
        """
        if request.path != "/api/health_check":
            session.permanent = True
            session['username'] = USERNAME
            session.modified = True

        return res

    return app


def __register_api(app):
    """
    Private method to register all the API endpoints for this app.
    Automatically called in the create_app method.

    Parameters
    ----------
    app : Flask
        The Flask app which has its endpoints set before running
    """

    api.app = app

    # Imports for controller classes must be done after app is initialized
    from .controllers.user_controller import UserAccount, UserLogin, \
        UserHome, UserLogout
    from .controllers.health_check_controller import HealthCheck
    from .controllers.course_controller import CourseModify, EnrollStudent, CourseScheduleView, CourseGradeModify

    # Adds API routes from the controller classes to the app
    api.add_resource(UserAccount, "/api/user")
    api.add_resource(UserLogin, "/api/login")
    api.add_resource(UserLogout, "/api/logout")
    api.add_resource(UserHome, "/", "/index")
    api.add_resource(HealthCheck, "/api/health_check")
    api.add_resource(CourseModify, "/api/course")
    api.add_resource(EnrollStudent, "/api/mapping")
    api.add_resource(CourseGradeModify, "/api/mapping/grade")
    api.add_resource(CourseScheduleView, "/api/schedule")


def get_role():
    """
    Gets the role value of this app instance.
    :return: role of the user
    """
    return ROLE


def set_username(username):
    """
    Sets the global USERNAME variable to the username of the logged in user.
    :param username: the username of the user
    """
    global USERNAME
    USERNAME = username


def get_username():
    """
    Gets the username of the logged in user for this session.
    :return: the logged in user's username
    """
    return USERNAME

