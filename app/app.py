from flask import Flask
from routes.docs import docs_bp
from routes.stackoverflow import stackoverflow_bp
from config import Config
from models import db

app = Flask(__name__)

app.register_blueprint(docs_bp, url_prefix="/docs")
app.register_blueprint(stackoverflow_bp, url_prefix="/stackoverflow")
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
