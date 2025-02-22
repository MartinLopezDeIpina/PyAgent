from flask import Blueprint
from src.models.Doc import DocClass
from src.services.docs import add_library_to_docs, rag_docs_functions

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/doc_rag/<library_name>/<query>', methods=['GET'])
def rag_functions(library_name: str, query: str):
    doc_classes = DocClass.query.filter_by(library=library_name).first()
    if not doc_classes:
        add_library_to_docs(library_name)

    return rag_docs_functions(library_name, query)
