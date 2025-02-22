from sqlalchemy import ForeignKeyConstraint
from src.models import db
from pgvector.sqlalchemy import Vector

class DocClass(db.Model):
    __tablename__ = 'doc_class'
    __table_args__ = {'schema': 'python_tools'}

    library = db.Column(db.String(50), primary_key=True)
    class_name = db.Column(db.String(50), primary_key=True)
    class_doc = db.Column(db.Text)
    embedding = db.Column(Vector(384))

    functions = db.relationship('DocFunction', backref='doc_class', lazy=True)

class DocFunction(db.Model):
    __tablename__ = 'doc_function'
    __table_args__ = (
        ForeignKeyConstraint(
            ['library', 'class_name'],
            ['python_tools.doc_class.library', 'python_tools.doc_class.class_name']
        ),
        {'schema': 'python_tools'}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    function_name = db.Column(db.String(1024))
    function_doc = db.Column(db.Text)
    embedding = db.Column(Vector(384))

    library = db.Column(db.String(50))
    class_name = db.Column(db.String(50))


