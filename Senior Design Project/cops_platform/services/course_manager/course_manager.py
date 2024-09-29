"""Course Manager

This is the runner of the Course Manager service.

How to Run:
Set the environment variable FLASK_APP to the following in order to run:
FLASK_APP=course_manager.py

Use the "flask run" command to start this app.

Environment Variables:
This app takes in many environment variables that can be viewed in the config.py class in the course_manager directory.

FLASK_CONFIG:
Set the FLASK_CONFIG environment variable to the database config settings wanted.
'testing' and 'default' uses the sqlite database that is automatically created.
'development' uses the postgresql database. Must know all environment variables in order to create a path to DB.
(These needed variables are listed in the PostgresConfig class in config.py in the course_manager module)


ROLE:
Set the ROLE environment variable based on the role of the user to be logged in (corresponds to their security context)
Defaults to student role if none is provided (least privilege)
Role Coordinator = 'coordinator'
Role Instructor = 'instructor'
Role Student = 'student'


This module imports the create_app factory method from app.py (located at __init__.py in the app directory).
This initializes the Flask course_manager app settings and then runs this app.
"""

from .app import create_app
import os

config = os.getenv('FLASK_CONFIG') or 'default'
role = os.getenv('ROLE') or 'student'
app = create_app(config, role)
