from . import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True) # Unique para evitar duplicados en el panel
    rol = db.Column(db.String(20), default='OPERADOR') # DUEÑO, CAJA, COCINA
    activo = db.Column(db.Boolean, default=True) # <--- NUEVO: Para "bloquear" en vez de borrar
    
    # Relaciones
    # Un usuario puede tener varios dispositivos (ej: su celular y una tablet)
    tokens = db.relationship('TokenAcceso', backref='usuario', cascade="all, delete-orphan")
    acciones = db.relationship('Auditoria', backref='usuario')

class TokenAcceso(db.Model):
    __tablename__ = 'tokens_acceso'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    dispositivo = db.Column(db.String(50)) # Ej: "Samsung de Persona B"
    
    # <--- CAMBIO: nullable=True permite que el token exista antes de ser asignado a un usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50)) # 'CREAR', 'EDITAR', 'LOGIN_DISPOSITIVO'
    tabla_afectada = db.Column(db.String(50)) 
    registro_id = db.Column(db.Integer) 
    fecha_hora = db.Column(db.DateTime, default=datetime.now)

