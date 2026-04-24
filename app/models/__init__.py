from flask_sqlalchemy import SQLAlchemy

# 1. Instanciamos SQLAlchemy una sola vez para todo el proyecto
db = SQLAlchemy()

# 2. Importamos todos los modelos. 
# IMPORTANTE: Se importan DESPUÉS de instanciar 'db' para evitar errores.
from .usuario import Usuario, TokenAcceso, Auditoria
from .producto import Producto, Categoria
from .venta import Venta, ProductoVendido
from .caja import Caja, Egreso
