import sys

from flask import jsonify
from sentence_transformers import SentenceTransformer
from src.models import db
from src.models.Doc import DocClass, DocFunction
import importlib
import importlib.util
import inspect
import subprocess
import numpy as np

def add_library_to_docs(library_name: str):
    ensure_package(library_name)

    module = importlib.import_module(library_name)
    add_library_class_functions_to_db(library_name, module)

    add_class_and_function_embeddings(library_name)


def add_library_class_functions_to_db(library_name: str, module):
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__.startswith(module.__name__):
            class_name = obj.__name__
            class_doc = inspect.getdoc(obj) or ""

            existing_class = DocClass.query.filter_by(library=library_name, class_name=class_name).first()
            if existing_class:
                print(
                    f"La clase {class_name} de la librería {library_name} ya existe en la base de datos. Omitiendo...")
                continue

            print(f"añadiendo clase {class_name} de librería {library_name}")
            doc_class_obj = DocClass(
                library=library_name,
                class_name=class_name,
                class_doc=class_doc
            )
            db.session.add(doc_class_obj)

            for method_name, method_obj in inspect.getmembers(obj):
                if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                    if not method_name.startswith("__"):
                        method_doc = inspect.getdoc(method_obj) or ""
                        signature = str(inspect.signature(method_obj))
                        full_function_name = f"{method_name}{signature}"

                        print(f"añadiendo función {full_function_name} de clase {class_name} de librería {library_name}")
                        doc_function_obj = DocFunction(
                            function_name = full_function_name,
                            function_doc=method_doc,
                            library=library_name,
                            class_name=class_name
                        )
                        doc_class_obj.functions.append(doc_function_obj)
                        db.session.add(doc_function_obj)

    db.session.commit()

def ensure_package(library_name: str):
    if importlib.util.find_spec(library_name) is None:
        print(f"installing package {library_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])
    else:
        print(f"package {library_name} already installed")

def add_class_and_function_embeddings(library_name: str):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    batch_size = 128

    doc_classes = DocClass.query.filter_by(library=library_name).all()
    for i in range(0, len(doc_classes), batch_size):
        print(f"processing class batch {i} / {len(doc_classes)}")
        batch = doc_classes[i:i+batch_size]
        class_docs = [doc_class.class_doc for doc_class in batch]

        class_embeddings = model.encode(class_docs)
        for j, class_doc in enumerate(batch):
            class_doc.embedding = class_embeddings[j]
    db.session.commit()

    doc_functions = DocFunction.query.filter_by(library=library_name).all()
    for i in range(0, len(doc_functions), batch_size):
        print(f"processing function batch {i} / {len(doc_functions)}")
        batch = doc_functions[i:i+batch_size]
        function_docs = [doc_function.function_doc for doc_function in batch]

        function_embeddings = model.encode(function_docs)
        for j, function_doc in enumerate(batch):
            class_embedding = batch[j].doc_class.embedding
            avg_embedding = np.mean(np.vstack((class_embedding, function_embeddings[j])), axis=0)
            function_doc.embedding = avg_embedding

    db.session.commit()

def rag_docs_functions(library_name: str, query: str, top_k = 10):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query)

    results = db.session.query(DocFunction).filter(
        DocFunction.library == library_name
    ).order_by(DocFunction.embedding.cosine_distance(query_embedding)).limit(top_k).all()

    results_class_grouped = {}
    for doc_function in results:
        class_name = doc_function.class_name

        if class_name not in results_class_grouped:
            results_class_grouped[class_name] = {
                "class_name": class_name,
                "class_doc": doc_function.doc_class.class_doc,
                "functions": []
            }

        results_class_grouped[class_name]["functions"].append({
            "function_name": doc_function.function_name,
            "function_doc": doc_function.function_doc
        })

    return jsonify(list(results_class_grouped.values()))





