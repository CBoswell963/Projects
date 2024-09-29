"""
Model class that represents the course table in the database

Imports the db object from the course_manager app class.
"""

from ...app import db


class Course(db.Model):
    """
    Extends the SQLAlchemy model class.

    Course's have a unique id, a unique name, days (String value of days of week; ex: "MW"), start_time (Time object),
    and end_time (Time object).
    
    Many to one relationship with an Instructor (foreign key is the instructor's id)
    One to many relationship with CourseStudentMapping (mappings are referenced as a list of these
    CourseStudentMapping objects)
    """
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    days = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    course_mappings = db.relationship('CourseStudentMapping', backref='mapping', lazy=True, cascade="all, delete-orphan")
