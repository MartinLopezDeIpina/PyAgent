from flask import Blueprint
from models.Doc import DocClass, DocFunction
from services.docs import add_library_to_docs, rag_docs_functions

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/<library_name>', methods=['GET'])
def hw_docs(library_name):
    doc_classes = DocClass.query.filter_by(library=library_name).first()
    if not doc_classes:
        add_library_to_docs(library_name)
        return "Library added to docs"
    else:
        return doc_classes.class_doc

@docs_bp.route('/doc_rag/<library_name>/<query>', methods=['GET'])
def rag_functions(library_name: str, query: str):
    return rag_docs_functions(library_name, query)
