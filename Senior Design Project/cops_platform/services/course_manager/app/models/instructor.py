"""
Model class that represents the instructor table in the database.

Imports the db object from the course_manager app class.
"""

from ...app import db


class Instructor(db.Model):
    """
    Extends the SQLAlchemy model class.

    Instructor's have an unique id (primary key), unique username, and name.
    
    One to many relationship with Course (courses are referenced as a list of these Course objects)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    courses = db.relationship('Course', backref='professor', cascade="all, delete-orphan")
