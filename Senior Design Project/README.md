# 2020SpringTeam32

# How to run course_manager.py

Set the FLASK_APP python variable to course_manager.py

Linux/Unix:  
```console
$ export FLASK_APP=course_manager.py
```
Windows:  
```console
$ set FLASK_APP=course_manager.py
```

Now use the following command to start the Course Manager Flask application:
```console
$ flask run
```
The Flask Application should now be running on your localhost at port 5000 (These are the default settings).  

NOTE: You must be either be inside the course_manager directory or have the PYTHONPATH variable include the course_manager directory in order for the "flask run" command to work.


Example for Linux/Unix:  
```console
$ export PYTHONPATH=/home/jballie/PycharmProjects/2020SpringTeam32/cops_platform/services/course_manager
```
  
Windows:  
```console
$ set PYTHONPATH=/home/jballie/PycharmProjects/2020SpringTeam32/cops_platform/services/course_manager
```

***

# How to run coverage reports for unit tests

The nose module will be used to locate and run all unit tests that reside in our tests directory.

It will then make use of the coverage.py module to run a coverage report for all of these tests.

Run the following command, from the root directory "2020SpringTeam32", in a terminal to run all the unit tests and generate a coverage report:

```console
$ nosetests -w cops_platform/services/course_manager/tests/ --with-coverage --cover-package=cops_platform
```
NOTE: Similar to the above section, you must have the root directory of the project available in the PYTHONPATH. You must also be using this command from within this directory.

Linux/Unix:  
```console
$ export PYTHONPATH=/home/jballie/PycharmProjects/2020SpringTeam32
```
  
Windows:  
```console
$ set PYTHONPATH=/home/jballie/PycharmProjects/2020SpringTeam32
```

***

# Development Best Practices to Follow:

Our team will be using the Pycharm IDE for development of the COps platform.
These are guidelines to follow for getting your development environment started up in Pycharm, 
setting up a virtual envrionment, and general best practices to follow when coding and working
in a team with Python and GitHub.

## Using git and GitHub with Pycharm

### Cloning repo via Pycharm
The VCS option on the top bar of Pycharm contains all of the version control actions and settings.

To clone a repo in Pycharm, simply select VCS -> Get From Version Control... 

Now paste in the URL for our NCSU repo and then click the Clone button.


### Changing branches on Pycharm
VCS -> Git -> Branches.. will list all of the available branches remote and local that you can switch to.

If you are not update to date with some of the remote branches, remember to use Git -> Fetch

### Commiting, Pushing, and Pulling on Pycharm
All these commands are under VCS -> Git. This should all work similarly to Eclipse.


## Creating Virtual Environment in Pycharm
Using a virtual environment with projects is recommended because it helps to keep everyone working in a similar environment
with the same modules installed (along with not including libraries that we don't need for this project but you might have installed on your personal machine).

Use the following command in a terminal to create a virtual environment:<br/>
(NOTE: the terminal is located on one of the bottom tabs in Pycharm)
```console
$ python3 -m venv venv
```
Now using the following command to activate the virtual environment<br/>
On Linux:
```console
$ source venv/bin/activate
```

On Windows:
```console
$ venv\Scripts\activate
```

You should successfully be in your virtual environment!
Can confirm by seeing a prompt on the console similar to this:
```console
(venv) $ _
```

A final step is make sure Pycharm is using your virtual envrionment as it's python interpreter for this project.
To do this, in Pycharm go to Settings -> Project: "Project Name" -> Project Interpreter

Now click on the settings icon that is next to the Project Interpreter text box and click Add.

Make sure Virtualenv Environment is selected and then select the Existing Environment radio button.
Locate and select the python executable that is inside your venv directory as the Interpreter.
For example on Unbuntu, this is located in /venv/bin/python

Click Apply and then click OK.


## Installing Python Libaries:
The requirements.txt file will contain all of the dependencies we need for this project.

Use the following command to install any missing dependencies:
```console
pip install --user --requirement requirements.txt
```

This allows us all to easily be up to date with the libraries others have installed while developing.

Whenever you use pip to install a new library, use the following command:
```console
pip freeze > requirements.txt
```

This will update the requirements.txt with all python modules you have installed in your virtual environment.


## How to Run Flask
In order to run a Flask app you must set an environment variable to the location of the app you want to run.

For example, to run the postgres_service.py flask application, we would use the following command to set our current FLASK_APP to postgres_service.py:

On Linux:
```console
(venv) $ export FLASK_APP=postgres_service.py
```
On Windows:
```console
(venv) $ set FLASK_APP=postgres_service.py
```
Now to run this application, we would enter the following command on the terminal:
```console
(venv) $ flask run
```

NOTE: You might need to be in the same working directory of your targeted flask application (ex: postgres_service.py) in order for the flask run command to work.<br /><br /> 
***

# Resouces and Tutorials

## Flask
* https://flask.palletsprojects.com/en/1.1.x/quickstart/
* https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

## SQLAlchemy with Flask
* https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
* https://flask.palletsprojects.com/en/1.1.x/patterns/sqlalchemy/

