import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'sistema.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'clave-secreta-provisional'
    STATIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'app', 'templates')

