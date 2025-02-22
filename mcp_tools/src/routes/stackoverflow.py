from flask import Blueprint
from src.services.stackoverflow import rag_stackoverflow

stackoverflow_bp = Blueprint('stackoverflow', __name__)

@stackoverflow_bp.route('/rag_posts/<query>', methods=['GET'])
def rag_posts(query: str):
    return rag_stackoverflow(query)