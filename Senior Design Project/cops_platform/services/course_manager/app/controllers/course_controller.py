"""
Course Controller

Controller class for all course related functionality in Course Manager.
Contains endpoints to handle course modification, grade or roster modification
and viewing course schedules.

"""
from flask_restful import Resource, reqparse, abort
import datetime
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from ...app.utils.controller_util import abort_if_user_not_logged_in, \
    check_course_student_mapping, check_user_credentials, abort_if_access_denied
from ..models import Course, CourseStudentMapping, Student, Instructor
from ...app import db, get_role, get_username


class CourseModify(Resource):
    """
    Course Modification resource
    """
    def post(self):
        """
        Handles adding a new course from the Course Manager system.
        Requires the values for name, day, start time, end time and instructor are passed in the body of the request
        POST request
        :return: Response contains a status code with a message of whether the course addition was successful
        """
        # Returns error message if user not authenticated
        abort_if_user_not_logged_in()

        try:
            # Retrieves the arguments from the form body of this request
            parser = reqparse.RequestParser()
            parser.add_argument('name', location='form')
            parser.add_argument('days', location='form')
            parser.add_argument('start_time', location='form')
            parser.add_argument('end_time', location='form')
            parser.add_argument('instructor_username', location='form')
            args = parser.parse_args()

            # Converts the sent time strings to Time objects
            # Expects the time to be sent in the string format "HH:MM:
            # Example: "09:50"
            start_time = datetime.datetime.strptime(args.start_time, '%H:%M').time()
            end_time = datetime.datetime.strptime(args.end_time, '%H:%M').time()

            # Obtains the instructor's id based on the username given in the request
            instructor_id = Instructor.query.filter_by(username=args.instructor_username).first().id

            # Creates a new Course database object based on the request parameters
            course = Course(name=args.name, days=args.days, start_time=start_time, end_time=end_time,
                            instructor_id=instructor_id)

            # Attempts to add this course to the database
            db.session.add(course)
            db.session.commit()

        # Returns error message when exception occurs
        except IntegrityError:
            abort(400, message="A course with this name already exists.")
        except InvalidRequestError:
            abort(400, message="Invalid argument/s were provided for this course.")
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error handling the addition of this course.")

        # Returns success message
        return "Course successfully added!"

    def delete(self):
        """
        Handles deleting an existing course from the Course Manager system
        Requires the values for name, day, start time, end time and instructor are passed in as arguments
        in the body of the request
        DELETE request
        :return: Response contains a status code with a message of whether the deletion was successful
        """

        # Abort if user is not logged in
        abort_if_user_not_logged_in()

        try:
            # Retrieve the arguments from the form data of the request
            parser = reqparse.RequestParser()
            parser.add_argument('course_name', location='form')
            args = parser.parse_args()

            # Attempts to retrieve the course in the database with the matching course name sent in the request
            course = Course.query.filter_by(name=args.course_name).first()

            # Course does not exist with this name. Return error response.
            if course is None:
                abort(400, message="Deletion of course failed. A course with this name does not exist in the system.")

            # Try to delete this course from the database
            db.session.delete(course)
            db.session.commit()

        # Returns error message when exception occurs
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error handling the deletion of this course")

        # Returns success message
        return "Course successfully deleted!"


class EnrollStudent(Resource):
    """
    Student Enrollment Resource
    """
    def post(self):
        """
        Handles enrolling a student in a course from the Course Manager system.
        Requires the value for the student's username and the name of the course are passed in as parameters in the
        body of the request
        POST request
        :return: Response contains a status code with a message of whether the student enrollment was successful
        """
        # Returns error message is user not authenticated
        abort_if_user_not_logged_in()

        try:
            # Retrieves the arguments from the form body of this request
            parser = reqparse.RequestParser()
            parser.add_argument('username', location='form')
            parser.add_argument('course_name', location='form')
            args = parser.parse_args()

            # Retrieves the matching student database object based on the passed in username
            student = Student.query.filter_by(username=args.username).first()
            # Retrieves the matching course database object based on the passed in course name
            course = Course.query.filter_by(name=args.course_name).first()

            # Student does not exist with this username. Return error response.
            if student is None:
                abort(400, message="Enrollment failed. A student with this username does not exist in this system.")
            # Course does not exist with this name. Return error response.
            if course is None:
                abort(400, message="Enrollment failed. A course with name does not exist in the system.")

            # Create a new CourseStudentMapping
            mapping = CourseStudentMapping(student_id=student.id, course_id=course.id)

            # Attempts to add this course mapping to the database
            db.session.add(mapping)
            db.session.commit()

        # Returns error message when exception occurs
        except IntegrityError:
            abort(400, message="The student is already enrolled in this course")
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error with enrolling student")

        # Returns success message
        return "Student successfully enrolled!"


class CourseGradeModify(Resource):
    """
    Course Grade Modification resource
    """

    def put(self):
        """
        Handles updating a student's grade in the Course Manager system.
        Requires the value for the student's username and the name of the course are passed in as parameters in the
        body of the request
        PUT request
        :return: Response contains a status code with a message of whether the student's grade modification was
        successful
        """
        # Returns error message is user not authenticated
        abort_if_user_not_logged_in()
        try:
            # Retrieves the arguments from the form body of this request
            parser = reqparse.RequestParser()
            parser.add_argument('username', location='form')
            parser.add_argument('course_name', location='form')
            parser.add_argument('grade', location='form')
            args = parser.parse_args()

            # Retrieves the matching student database object based on the passed in username
            student = Student.query.filter_by(username=args.username).first()
            # Retrieves the matching course database object based on the passed in course name
            course = Course.query.filter_by(name=args.course_name).first()

            # Student does not exist with this username. Return error response.
            if student is None:
                abort(400, message="Grade modification failed. A student with this username does not exist in this system.")
            # Course does not exist with this name. Return error response.
            if course is None:
                abort(400, message="Grade modification failed. A course with name does not exist in the system.")

            # Retrieves the matching course student mapping from the database
            mapping = check_course_student_mapping(student_id=student.id, course_id=course.id)

            # Updates the grade and commits changes to database
            mapping.grade = args.grade
            db.session.commit()

        # Returns error message when exception occurs
        except InvalidRequestError:
            abort(400, message="Grade modification failed. Invalid parameters were provided in this request.")
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error with modifying student's grade")

        # Returns success message
        return "Student's grade successfully modified!"


class CourseScheduleView(Resource):
    """
    Course Schedule Viewing resource
    """
    def get(self):
        """
        Handles retrieving the course schedules for the user.
        Processes the course schedule based on the currently logged in user
        and their role.
        :return: a list of course schedule objects
        """
        # Returns error message is user not authenticated
        abort_if_user_not_logged_in()

        try:
            # Initializes course schedule list
            schedule = []
            # Obtains the role of this user
            role = get_role()
            # Obtains the username of this user
            username = get_username()

            # Processes the course schedule for a student
            if role == 'student':

                # Retrieves the user object for this logged in student
                user = check_user_credentials(username, role)

                # Retrieves the course student mappings for this student
                mappings = user.course_mappings

                # Creates a course object to add to the schedule for each course mapping
                for course_mapping in mappings:

                    # Retrieves the Course object that corresponds to this mapping
                    course_id = course_mapping.course_id
                    course = Course.query.filter_by(id=course_id).first()

                    # Retrieves the Instructor name for this course
                    # NOTE: For SELinux this requires a Student user to have read access to both the id and name
                    # columns for the Instructor table
                    instruct_name = Instructor.query.with_entities(Instructor.name).filter_by(id=course.instructor_id).\
                        first()[0]

                    # Creates an object with all of the course fields
                    course_fields = {"name": course.name, "days": course.days,
                                     "start_time": str(course.start_time), "end_time": str(course.end_time),
                                     "instruct_name": instruct_name, "grade": course_mapping.grade}

                    # Appends this course object to the student's schedule list
                    schedule.append(course_fields)

            # Processes the course schedule for an instructor
            elif role == 'instructor':

                # Retrieves the user object for this logged in instructor
                user = check_user_credentials(username, role)

                # Retrieves the courses this instructor teaches
                courses = user.courses

                # Adds a course object to the schedule for each course
                for course in courses:
                    # Initializes list of students for this course
                    students = []
                    # Retrieves all of the course student mappings for this course
                    student_mappings = CourseStudentMapping.query.filter_by(course_id=course.id).all()

                    # Adds each student name that is enrolled in this course to the list
                    for stu in student_mappings:
                        # NOTE: For SELinux this requires an Instructor user to have read access to both the id and name
                        # columns for the Student table
                        name = Student.query.with_entities(Student.name).filter_by(id=stu.student_id).first()[0]
                        students.append(name)

                    # Creates an object with all of the course fields
                    course_fields = {"name": course.name, "days": course.days,
                                     "start_time": str(course.start_time), "end_time": str(course.end_time),
                                     "students": students}

                    # Appends this course object to the instructor's schedule list
                    schedule.append(course_fields)

        # Returns error message if an exception occurs
        except Exception as inst:
            abort_if_access_denied(inst)
            abort(400, message="Error with viewing the schedule of this user")

        # Returns the course schedule as JSON, along with a success status
        return schedule, 200
