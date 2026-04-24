from . import db
from datetime import datetime

class Caja(db.Model):
    __tablename__ = 'caja'

    id_caja = db.Column(db.Integer, primary_key=True)
    # Fecha única por registro para evitar duplicados el mismo día
    fecha = db.Column(db.String(10), nullable=False, unique=True, default=lambda: datetime.now().strftime("%d-%m-%Y"))
    
    saldo_inicial = db.Column(db.Integer, default=0)
    saldo_final_efectivo = db.Column(db.Integer, default=0) # Lo que cuentan a mano
    
    # Totales calculados para el informe
    movimientos_efectivo = db.Column(db.Integer, default=0)
    movimientos_tarjeta = db.Column(db.Integer, default=0)
    movimientos_transferencia = db.Column(db.Integer, default=0)
    
    diferencia_efectivo = db.Column(db.Integer, default=0) # Cuadratura
    observaciones = db.Column(db.Text)
    
    # Estado para saber si el día terminó
    estado_caja = db.Column(db.String(10), default='ABIERTA') # 'ABIERTA' o 'CERRADA'
    
    # Relación con el usuario que hace el cierre (opcional pero recomendado)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

class Egreso(db.Model):
    __tablename__ = 'egresos'

    id_egreso = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Integer, nullable=False)
    descripcion_egreso = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # Insumos, Propinas, etc.
    
    fecha_egreso = db.Column(db.String(10), default=lambda: datetime.now().strftime("%d-%m-%Y"))
    hora_egreso = db.Column(db.String(5), default=lambda: datetime.now().strftime("%H:%M"))
    
    # Vinculamos el egreso a un usuario para saber quién sacó el dinero
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
