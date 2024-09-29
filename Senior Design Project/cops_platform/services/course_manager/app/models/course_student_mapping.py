"""
Model class that represents the course_student_mapping table in the database.

Imports the db object from the course_manager app class.
"""

from ...app import db


class CourseStudentMapping(db.Model):
    # Creates a unique constraint for this mapping's student_id and course_id
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),
    )
    """
    Extends the SQLAlchemy model class.
    
    CourseStudentMapping's have an unique id (primary key), and grade (Float value, ex: 3.5)
    CourseStudentMapping's have an unique combination for their student_id and course_id.
    
    Many to one relationship with an Student(foreign key is the student's id)
    Many to one relationship with a Course (foreign key is the course's id)
    """
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Float)
