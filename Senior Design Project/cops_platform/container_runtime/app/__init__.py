from flask import Flask
from .extensions import api
from flask_cors import CORS
from ..config import config
from flask_sqlalchemy import SQLAlchemy
import docker

# Global object for communicating with the database
db = SQLAlchemy()
# Global Docker Client object that is used to communicate with the Docker Daemon
DOCKER_CLIENT = None
# Global boolean for whether this application is working with SELinux enforced
ENFORCED = False


def create_app(config_name='default'):
    """
    Factory method for creating and returning a Flask app with all its required
    configurations and settings.

    Returns
    -------
    app : Flask
        the Flask app with all initialized settings and values
    """
    app = Flask(__name__)

    # Sets the configurations for this app based on the passed in config_name string value
    # NOTE: For now, just using the 'default' config_name string as there is only one config setting
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # By default allows CORS for all domains on all routes
    # NOTE: In a real application would want to restrict this to specific addresses
    # "support_credentials=True" allows CORS to pass a session cookie for authentication
    CORS(app, supports_credentials=True)

    # Initializes the api object
    api.init_app(app)

    # Initializes the db object for this app
    db.init_app(app)

    # Create the global docker client from the environment
    global DOCKER_CLIENT
    DOCKER_CLIENT = docker.from_env()

    # Registers the api endpoints for this app
    __register_api(app)

    # Set whether SELinux is enforced or not
    global ENFORCED

    # Sets whether this application will be running with SELinux
    # NOTE: Would likely not want this option in a real application
    # but it makes testing easier for machines that don't support SELinux
    if app.config['ENFORCED']:
        print("Running with SELinux enforced")
        ENFORCED = True
    else:
        print("Running without SELinux enforced")

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
    from .controllers.service_controller import ServiceRequest

    # Adds API routes from the controller classes to the app
    api.add_resource(ServiceRequest, "/service_request")


def get_docker_client():
    """
    Gets the docker client
    :return: the docker client
    """
    return DOCKER_CLIENT


def get_enforced_status():
    """
    Gets the SELinux enforced status of this running application
    :return: Whether this application is running with SELinux enforced
    """
    return ENFORCED
