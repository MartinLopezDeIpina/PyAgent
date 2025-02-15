from src.models import db
from pgvector.sqlalchemy import Vector

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'python_tools'}

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(384))
