"""
User Controller

Controller class for all user related functionality in Course Manager.
Contains endpoints to handle logging in, logging out, viewing account details, adding a new user,
and deleting an existing user.

"""

from flask import session, request, abort
from flask_restful import Resource, reqparse, abort
from sqlalchemy.exc import IntegrityError
from markupsafe import escape
from ..models import Student, Instructor, Coordinator
from ...app import db, get_role, set_username
from ...app.utils.controller_util import check_user_credentials, \
    abort_if_user_not_logged_in, abort_if_access_denied


class UserHome(Resource):
    """
    Home resource for the user.
    """

    def get(self):
        """
        GET request to the index or home page.
        :return: Returns response letting user know if they are logged in or not
        """
        if 'username' in session:
            return 'Logged in as %s' % escape(session['username'])
        abort(400, message='You are not logged in')


class UserLogin(Resource):
    """
    Login resource for the user.
    """

    def post(self):
        """
        POST request to the login page.
        The username of the user is expected as an argument in the form of the request.
        :return:
        """
        # Obtains the username in the form of the request
        username = request.form['username']

        # Gets the role of this user
        role = get_role()

        # Checks the user's credentials in the database, method aborts if no match is found
        check_user_credentials(username, role)

        # Sets the username for this session to the now logged in user
        set_username(username)
        session['username'] = username
        session.permanent = True
        session.modified = True

        return "Successfully logged in"


class UserLogout(Resource):
    """
    Logout resource for the user.
    """

    def get(self):
        """
        GET request to the logout page.
        :return:
        """
        # Sends error message if user is not logged
        abort_if_user_not_logged_in()

        # Remove the user's name from this session; they are now logged out
        session.pop('username', None)
        set_username(None)
        session.permanent = True
        session.modified = True

        return "Successfully logged out"


class UserAccount(Resource):
    """
    Handles requests for user accounts.
    """

    def get(self):
        """
        Handles viewing the logged in user's account information
        GET request
        :return: Response contains the user's id, username, and name in the data field.
        """
        # Gets the role of this user
        role = get_role()

        # Returns error message is user not authenticated
        abort_if_user_not_logged_in()

        # Retrieves the user from the database
        user = check_user_credentials(session["username"], role)

        # Account details to been send back as JSON
        acct_details = {'id': user.id, 'username': user.username, 'name': user.name}

        # If this user is a student, calculates their GPA and adds to account details
        # NOTE: The gpa field is currently not being used in the database. Since instructor's
        # do not have write access to the Student's table and columns with our current SELinux
        # policy, the student's gpa could not be updated when a single grade is modified by
        # an Instructor. This is why we are re-calculating this every time the Student requests
        # their account details. Would likely want to update how this policy works.
        if role == "student":
            gpa = calculate_gpa(user)
            acct_details['gpa'] = gpa

        # Returns the user's account details
        return acct_details

    def post(self):
        """
        Handles adding a new user from the Course Manager system.
        Requires the values for username, name, and role are passed in the body of the request
        POST request
        :return: Response contains a status code with a message of whether the user addition was successful
        """

        # Aborts if the user is not authenticated
        abort_if_user_not_logged_in()

        try:
            # Retrieves the arguments from the form body of this request
            parser = reqparse.RequestParser()
            parser.add_argument('username', location='form')
            parser.add_argument('name', location='form')
            parser.add_argument('role', location='form')
            args = parser.parse_args()
            user = None

            # Creates a specific user type based on their role
            if args.role == 'student':
                user = Student(username=args.username, name=args.name)
            elif args.role == 'instructor':
                user = Instructor(username=args.username, name=args.name)
            elif args.role == 'coordinator':
                user = Coordinator(username=args.username, name=args.name)

            # Attempts to add this user to the database
            db.session.add(user)
            db.session.commit()

        # Returns error message when exception occurs
        except IntegrityError:
            abort(400, message="Failed to add a new user. A user with this username already exists in the system.")
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error with adding user.")

        # Returns success message
        return "User successfully added!"

    def delete(self):
        """
        Handles deleting an existing user from the Course Manager system
        Requires the values for username and role are passed in as arguments in the body of the request
        DELETE request
        :return: Response contains a status code with a message of whether the deletion was successful
        """

        # Abort if user is not logged in
        abort_if_user_not_logged_in()

        try:
            # Retrieve the arguments from the form data of the request
            parser = reqparse.RequestParser()
            parser.add_argument('username', location='form')
            parser.add_argument('role', location='form')
            args = parser.parse_args()

            # Retrieve user based on arguments given in request
            user = check_user_credentials(args.username, args.role)

            # Try to delete this user from the database
            db.session.delete(user)
            db.session.commit()

        # Returns error message when exception occurs
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error with deleting user")

        # Returns success message
        return "User successfully deleted!"


def calculate_gpa(user):
    """
    Calculates the gpa for the student.
    NOTE: Is not an accurate GPA calculator. Is merely mocking
    how this could work in a real application.
    :param user: the student user
    :return: the gpa for this student
    """
    num_classes = len(user.course_mappings)
    total_grade_amt = 0.0

    # Obtains all the course mappings for the student
    for mapping in user.course_mappings:
        if mapping.grade is None:
            num_classes = num_classes - 1
        else:
            total_grade_amt = total_grade_amt + mapping.grade

    # Return 0.0 if student has no classes or grades for these classes
    if num_classes <= 0:
        return 0.0

    return total_grade_amt/num_classes
