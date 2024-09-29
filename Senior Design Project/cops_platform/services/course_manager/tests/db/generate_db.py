"""
Database Generator

This a script with helper methods for resetting the state of the database and adding mock
data for testing purposes.

This script also labels all the database with our SELinux Security Policy if the
ENFORCED environment variable is set to any arbitrary value.

This file can also be imported as a module and contains the following
functions:
    * reset_database - drops the database and then creates it - resets database tables
    * add_mock_data - adds mock data to the database
"""

from cops_platform.services.course_manager.app import create_app, db
from cops_platform.services.course_manager.app.models import Student, Coordinator, Instructor, CourseStudentMapping, \
    Course
from datetime import time
import os


def main(config='default'):
    """
    Creates a new instance of the app, resets database, and add mocks data.
    """
    app = create_app(config)
    app_context = app.app_context()
    app_context.push()
    reset_database()    
    add_mock_data()

    # Only labels the database if the enforced SELinux env is set
    if os.getenv("ENFORCED"):
        label_all()
    app_context.pop()


def reset_database():
    """
    Resets state of the database by dropping all tables and then recreating them based
    on the db.Model classes in the models package.
    """
    db.drop_all()
    db.create_all()


def add_mock_data():
    """
    Add mock data to the database.
    """
    student = Student(username="student", name="Student")
    db.session.add(student)
    db.session.commit()

    coordinator = Coordinator(username="coordinator", name="Coordinator")
    db.session.add(coordinator)
    db.session.commit()

    instructor = Instructor(username="instructor", name="Instructor")
    db.session.add(instructor)
    db.session.commit()

    instructor = Instructor.query.filter_by(username=instructor.username).first()
    start = time(12, 30)
    end = time(2, 15)
    course = Course(name="CSC316", days="MW", start_time=start, end_time=end, instructor_id=instructor.id)
    db.session.add(course)
    db.session.commit()

    student = Student.query.filter_by(username=student.username).first()
    course = Course.query.filter_by(name=course.name).first()
    mapping = CourseStudentMapping(grade="4.0", course_id=course.id, student_id=student.id)
    db.session.add(mapping)
    db.session.commit()

    db.session.remove()


def label_all():
    """
    A function for labeling all the objects in the database
    """
    sec_label("table", "course", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.id", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.instructor_id", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.name", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.days", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.start_time", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course.end_time", "system_u:object_r:course_data_t:s0")
    
    sec_label("table", "course_student_mapping", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course_student_mapping.id", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course_student_mapping.student_id", "system_u:object_r:course_data_t:s0")
    sec_label("column", "course_student_mapping.course_id", "system_u:object_r:course_data_t:s0")
    
    sec_label("column", "course_student_mapping.grade", "system_u:object_r:grade_data_t:s0")
    
    sec_label("table", "coordinator", "system_u:object_r:coordinator_data_t:s0")
    sec_label("column", "coordinator.id", "system_u:object_r:coordinator_data_t:s0")
    sec_label("column", "coordinator.username", "system_u:object_r:coordinator_data_t:s0")
    sec_label("column", "coordinator.name", "system_u:object_r:coordinator_data_t:s0")
    
    sec_label("table", "instructor", "system_u:object_r:instructor_data_t:s0")
    sec_label("column", "instructor.username", "system_u:object_r:instructor_data_t:s0")

    sec_label("column", "instructor.id", "system_u:object_r:course_data_t:s0")    
    sec_label("column", "instructor.name", "system_u:object_r:course_data_t:s0")
    
    sec_label("table", "student", "system_u:object_r:student_data_t:s0")
    
    sec_label("column", "student.username", "system_u:object_r:course_data_t:s0")
    sec_label("column", "student.id", "system_u:object_r:course_data_t:s0")    
    sec_label("column", "student.name", "system_u:object_r:course_data_t:s0")


def sec_label(type, name, label):
    """
    A function for labeling data in the database
    """
    # I was unable to parametrize this query with the mechanisms provided by SQLAlchemy
    db.session.execute("SECURITY LABEL ON " + type + " " + name + " IS " + "'" + label + "'")
    db.session.commit()


# If this is run as a python script, calls its main method
if __name__ == "__main__":
    app_config = os.getenv('FLASK_CONFIG') or 'default'
    main(app_config)

