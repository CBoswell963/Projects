#!/bin/sh
# This shell script is called when the course_manager container boots

# Activates the virtual environment which contains the needed dependencies for this app
source venv/bin/activate

# Runs the Course Manager flask application. Host command allows app to be accessed externally
flask run --host=0.0.0.0



