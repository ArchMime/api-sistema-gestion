from flask import Flask
from flask_cors import CORS
from config import Config
from app.models import db

def create_app():
    app = Flask(__name__, 
                static_folder=Config.STATIC_FOLDER,
                template_folder=Config.TEMPLATE_FOLDER)
    
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    @app.route('/')
    def index():
        return "¡Motor configurado correctamente!"

    return app

