# app/__init__.py
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

    # Importamos los Blueprints aquí dentro para evitar errores de NameError o Ciclos
    from app.controllers.venta_controller import venta_bp
    from app.controllers.producto_controller import producto_bp
    from app.controllers.caja_controller import caja_bp
    from app.controllers.auth_controller import auth_bp

    # Registramos los Blueprints con prefijo /api
    # Nota: He ajustado los nombres para que coincidan con la variable definida en los controllers
    app.register_blueprint(venta_bp, url_prefix='/api/ventas')
    app.register_blueprint(producto_bp, url_prefix='/api/productos')
    app.register_blueprint(caja_bp, url_prefix='/api/caja')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
