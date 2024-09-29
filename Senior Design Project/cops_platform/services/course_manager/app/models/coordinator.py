"""
Model class that represents the coordinator table in the database.

Imports the db object from the course_manager app class.
"""

from ...app import db


class Coordinator(db.Model):

    """
    Extends the SQLAlchemy model class.

    Coordinator's have an unique id (primary key), unique username, and name.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
