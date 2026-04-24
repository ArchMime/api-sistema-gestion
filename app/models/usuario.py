from . import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), default='OPERADOR') # DUEÑO, CAJA, COCINA
    
    # Relaciones
    tokens = db.relationship('TokenAcceso', backref='usuario', cascade="all, delete-orphan")
    acciones = db.relationship('Auditoria', backref='usuario')

class TokenAcceso(db.Model):
    __tablename__ = 'tokens_acceso'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    dispositivo = db.Column(db.String(50)) # Ej: "iPhone de Persona A"
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50)) # 'CREAR', 'EDITAR', 'ELIMINAR'
    tabla_afectada = db.Column(db.String(50)) # 'productos', 'ventas', etc.
    registro_id = db.Column(db.Integer) # El ID del movimiento
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
