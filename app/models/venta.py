from . import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'

    id_venta = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False, default="Consumo Local")
    total = db.Column(db.Integer, nullable=False, default=0)
    estado_pago = db.Column(db.String(20), nullable=False, default='PENDIENTE') # PENDIENTE, PAGADO, ANULADO
    forma_pago = db.Column(db.String(20)) # EFECTIVO, TARJETA, TRANSFERENCIA
    propina = db.Column(db.Integer, default=0)

    # Tiempos
    fecha_venta = db.Column(db.String(10), default=lambda: datetime.now().strftime("%d-%m-%Y"))
    hora_venta = db.Column(db.String(5), default=lambda: datetime.now().strftime("%H:%M"))

    # --- CONEXIONES CRÍTICAS ---
    # Usuario que registró la venta
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Caja a la que pertenece esta venta (Vínculo vital para el arqueo)
    id_caja_fk = db.Column(db.Integer, db.ForeignKey('caja.id_caja'), nullable=False)

    # Relación para acceder a los productos de esta venta
    detalles = db.relationship('ProductoVendido', backref='venta', cascade="all, delete-orphan")

class ProductoVendido(db.Model):
    __tablename__ = 'productos_vendidos'

    id_detalle = db.Column(db.Integer, primary_key=True)

    id_venta_fk = db.Column(db.Integer, db.ForeignKey('ventas.id_venta', ondelete='CASCADE'), nullable=False)
    
    # RESTRICT: No permite borrar un producto si ya tiene ventas registradas
    id_producto_fk = db.Column(db.Integer, db.ForeignKey('productos.codigo_producto', ondelete='RESTRICT'), nullable=False)
    producto = db.relationship('Producto', backref='ventas_donde_aparece')
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False) # Precio histórico al momento de vender

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
