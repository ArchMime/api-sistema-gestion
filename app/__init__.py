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

    with app.app_context():
        # Esto asegura que las nuevas tablas (Caja, Ventas, etc.) 
        # se creen automáticamente si no existen.
        db.create_all()

    # Importamos los Blueprints
    from app.controllers.venta_controller import venta_bp
    from app.controllers.producto_controller import producto_bp
    from app.controllers.caja_controller import caja_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.config_controller import config_bp
    app.register_blueprint(config_bp, url_prefix='/api/configuracion')

    # Registro de rutas con prefijo /api
    app.register_blueprint(venta_bp, url_prefix='/api/ventas')
    app.register_blueprint(producto_bp, url_prefix='/api/productos')
    app.register_blueprint(caja_bp, url_prefix='/api/caja')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
