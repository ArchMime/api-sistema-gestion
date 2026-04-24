from . import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relación: permite acceder a todos los productos de esta categoría
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    codigo_producto = db.Column(db.Integer, primary_key=True)
    nombre_producto = db.Column(db.String(100), nullable=False)
    precio_producto = db.Column(db.Integer, nullable=False)
    descripcion_producto = db.Column(db.Text)
    formato_producto = db.Column(db.String(50))
    
    # Llave foránea hacia Categoría
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
