from flask import Flask
from src.routes.docs import docs_bp
from src.routes.stackoverflow import stackoverflow_bp
from src.config import Config
from src.models import db
from src.models.Doc import DocClass, DocFunction
from src.models.Post import Post

app = Flask(__name__)

app.register_blueprint(docs_bp, url_prefix="/docs")
app.register_blueprint(stackoverflow_bp, url_prefix="/stackoverflow")
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
