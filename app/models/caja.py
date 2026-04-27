from . import db
from datetime import datetime

class Caja(db.Model):
    __tablename__ = 'caja'

    id_caja = db.Column(db.Integer, primary_key=True)
    
    # IMPORTANTE: Se quitó unique=True para permitir múltiples sesiones si se desea,
    # o para que la lógica de "Reapertura" del Service no choque con restricciones de BD.
    fecha = db.Column(db.String(10), nullable=False, default=lambda: datetime.now().strftime("%d-%m-%Y"))
    
    hora_apertura = db.Column(db.String(5), default=lambda: datetime.now().strftime("%H:%M"))
    hora_cierre = db.Column(db.String(5))

    saldo_inicial = db.Column(db.Integer, default=0)
    saldo_final_efectivo = db.Column(db.Integer, default=0) 

    # Totales acumulados
    movimientos_efectivo = db.Column(db.Integer, default=0)
    movimientos_tarjeta = db.Column(db.Integer, default=0)
    movimientos_transferencia = db.Column(db.Integer, default=0)

    diferencia_efectivo = db.Column(db.Integer, default=0) 
    observaciones = db.Column(db.Text)

    # 'ABIERTA' o 'CERRADA'
    estado_caja = db.Column(db.String(10), default='ABIERTA')

    # Usuario responsable
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # RELACIONES: Permiten al Service hacer caja.ventas o caja.egresos
    ventas = db.relationship('Venta', backref='caja', lazy=True)
    egresos = db.relationship('Egreso', backref='caja', lazy=True)


class Egreso(db.Model):
    __tablename__ = 'egresos'

    id_egreso = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Integer, nullable=False)
    descripcion_egreso = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

    fecha_egreso = db.Column(db.String(10), default=lambda: datetime.now().strftime("%d-%m-%Y"))
    hora_egreso = db.Column(db.String(5), default=lambda: datetime.now().strftime("%H:%M"))

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Vínculo con la sesión de caja específica
    id_caja_fk = db.Column(db.Integer, db.ForeignKey('caja.id_caja'), nullable=False)
