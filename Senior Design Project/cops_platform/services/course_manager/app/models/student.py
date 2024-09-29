"""
Model class representing the student table in the database.

Imports the initialized db object from the course_manager app class.
"""

from ...app import db


class Student(db.Model):
    """
    Extends the SQLAlchemy model class.

    Student's have an unique id (primary key), unique username, name, and gpa (Float value; ex: 4.0).
    
    One to many relationship with CourseStudentMappings (course_mappings are referenced as a list of these
    CourseStudentMapping objects)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    gpa = db.Column(db.Float, unique=False, nullable=True)
    course_mappings = db.relationship('CourseStudentMapping', backref='course', lazy=True, cascade="all, delete-orphan")
