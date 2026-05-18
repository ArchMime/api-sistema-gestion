"""Módulo de Configuración Global del Sistema de Gestión.

Este módulo define los parámetros operativos de la aplicación Flask, incluyendo
las credenciales criptográficas, la persistencia en SQLite y la vigencia infinita
de firmas JWT para terminales locales de punto de venta.
"""

import os


class Config:
    """Centraliza las variables de entorno y constantes del servidor local.

    Attributes:
        BASE_DIR (str): Ruta absoluta del directorio raíz del proyecto.
        SQLALCHEMY_DATABASE_URI (str): URI de conexión para el motor SQLite.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Desactiva el sistema de eventos 
            de SQLAlchemy para optimizar el consumo de memoria RAM.
        SECRET_KEY (str): Llave criptográfica para firmas de sesión nativas.
        STATIC_FOLDER (str): Ruta absoluta al directorio de recursos estáticos.
        TEMPLATE_FOLDER (str): Ruta absoluta al directorio de plantillas HTML.
        JWT_SECRET_KEY (str): Llave criptográfica para tokens simétricos JWT.
        JWT_ACCESS_TOKEN_EXPIRES (bool | int): Define la vigencia del JWT. Al ser
            False, los dispositivos del negocio no sufren desconexiones forzadas.
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'sistema.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'clave-secreta-provisional'
    STATIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'app', 'templates')
    
    # Configuración de JWT heredada del entorno o fallback por defecto
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'cambia-esto-en-produccion-local')
    JWT_ACCESS_TOKEN_EXPIRES = False
