from flask import jsonify
from sentence_transformers import SentenceTransformer

from src.models import db
from src.models.Post import Post


def rag_stackoverflow(query: str, top_k = 5):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query)

    results = db.session.query(Post).order_by(Post.embedding.cosine_distance(query_embedding)).limit(top_k).all()

    return jsonify([{
        "question": result.question,
        "body": result.body,
        "answer": result.answer
                     } for result in results])