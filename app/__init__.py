"""Módulo de Inicialización y Factoría de la Aplicación Flask.

Este módulo implementa el patrón Application Factory para orquestar la carga
de extensiones (SQLAlchemy, JWT, CORS), registrar los filtros de seguridad
de blocklist y mapear las rutas de la PWA local.
"""

from flask import Flask, render_template, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.models import db

# Instancia global única para el gestor criptográfico de tokens
jwt = JWTManager()


def create_app() -> Flask:
    """Fábrica de aplicaciones para inicializar los componentes de la API.

    Configura el entorno de ejecución local, enlaza la base de datos SQLite,
    establece los mecanismos de seguridad JWT y registra los controladores.

    Returns:
        Flask: Instancia completamente configurada de la aplicación web.
    """
    app = Flask(__name__,
                static_folder=Config.STATIC_FOLDER,
                template_folder=Config.TEMPLATE_FOLDER)

    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from app.services.seguridad_service import SeguridadService

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
        """Filtro de seguridad que valida la vigencia del token contra la BD.

        Args:
            jwt_header (dict): Contenedor de los metadatos de cabecera del JWT.
            jwt_payload (dict): Diccionario con los claims y datos del token.

        Returns:
            bool: True si el identificador JTI está explícitamente revocado
            en el almacén relacional; False en caso contrario.
        """
        jti = jwt_payload["jti"]
        return SeguridadService.verificar_jti_bloqueado(jti)

    with app.app_context():
        # Creación automática de tablas si no existen en el entorno local
        db.create_all()

    # Importación y registro de Blueprints con sus respectivos prefijos
    from app.controllers.venta_controller import venta_bp
    from app.controllers.producto_controller import producto_bp
    from app.controllers.caja_controller import caja_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.config_controller import config_bp

    app.register_blueprint(config_bp, url_prefix='/api/configuracion')
    app.register_blueprint(venta_bp, url_prefix='/api/ventas')
    app.register_blueprint(producto_bp, url_prefix='/api/productos')
    app.register_blueprint(caja_bp, url_prefix='/api/caja')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/')
    def index() -> str:
        """Sirve la página de inicio de la interfaz PWA.

        Returns:
            str: Contenido HTML renderizado del archivo index primario.
        """
        return render_template('index.html')

    return app
