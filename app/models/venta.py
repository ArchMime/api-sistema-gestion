from . import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'

    id_venta = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Integer, nullable=False, default=0)
    estado_pago = db.Column(db.String(20), nullable=False, default='PENDIENTE')
    forma_pago = db.Column(db.String(20)) # EFECTIVO, TARJETA, TRANSFERENCIA
    propina = db.Column(db.Integer, default=0)
    
    # Sello de tiempo automático
    fecha_venta = db.Column(db.String(10), default=lambda: datetime.now().strftime("%d-%m-%Y"))
    hora_venta = db.Column(db.String(5), default=lambda: datetime.now().strftime("%H:%M"))

    # Relación: permite hacer 'mi_venta.detalles' para ver los productos
    detalles = db.relationship('ProductoVendido', backref='venta', cascade="all, delete-orphan")

class ProductoVendido(db.Model):
    __tablename__ = 'productos_vendidos'

    id_detalle = db.Column(db.Integer, primary_key=True)
    
    # Vinculación con la Venta y el Producto
    id_venta_fk = db.Column(db.Integer, db.ForeignKey('ventas.id_venta', ondelete='CASCADE'), nullable=False)
    id_producto_fk = db.Column(db.Integer, db.ForeignKey('productos.codigo_producto', ondelete='RESTRICT'), nullable=False)
    
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False) # Guardamos el precio del momento de la venta
