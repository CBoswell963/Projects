"""
Controller Utils

Contains utility functions that are shared between the controller classes.

The following functions can be imported from this module:
    * abort_if_user_not_logged_in - authenticates user; checks whether the user is logged for this session
    * check_user_credentials - checks if there is matching user based on global role value. if so, returns user object
"""


from flask import session
from flask_restful import abort
from ...app.models import Student, Instructor, Coordinator, CourseStudentMapping


def abort_if_user_not_logged_in():
    """
    Authentication check for the user. If they are not logged in for this session, aborts this user request.
    """
    if 'username' not in session:
        abort(401, message="You are not authenticated")


def check_user_credentials(username, user_role):
    """
    Checks the credentials of the user and returns the user's information from the database.
    Aborts this user's request if no matching user is found.
    :param username: username of this user
    :param user_role: this user's role
    :return: the matching user object from the database.
    """
    user = None
    if user_role == "student":
        user = Student.query.filter_by(username=username).first()
    elif user_role == "instructor":
        user = Instructor.query.filter_by(username=username).first()
    elif user_role == "coordinator":
        user = Coordinator.query.filter_by(username=username).first()
    if user is None:
        abort(401, message="User does not exist in this system")

    return user


def check_course_student_mapping(student_id, course_id):
    """
    Checks if the specified student is on the roster for the given course
    :param student_id: username of the student
    :param course_id: course with all details
    :return: the matching course student mapping if it exists
    """
    course_student_mapping = CourseStudentMapping.query.filter_by(student_id=student_id, course_id=course_id).first()
    if course_student_mapping is None:
        abort(404, message="Student is not enrolled in this course as found in the system")
    return course_student_mapping


def abort_if_access_denied(err):
    """
    Checks if the exception contains and Insufficient Privilege message from SELinux.
    If it does, aborts and returns and "Access Denied" response to user.
    :param err: the error exception
    """
    if err and err.args and len(err.args) > 0:
        err_str = err.args[0]
        if 'psycopg2.errors.InsufficientPrivilege' in err_str:
            abort(401, message="Access Denied.")
