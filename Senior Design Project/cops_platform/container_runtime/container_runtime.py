"""
Container Runtime

This is the runner of the Container Runtime component.

How to Run:
Set the environment variable FLASK_APP to the following in order to run:
FLASK_APP=container_runtime.py

Use the "flask run" command to start this app.

This module imports the create_app factory method from app.py (located at __init__.py in the app directory).
This initializes the Flask course_manager app settings and then runs this app.
"""

from cops_platform.container_runtime.app import create_app

app = create_app()
