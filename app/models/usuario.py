"""Módulo de Modelos para la Gestión de Usuarios y Auditoría.

Este módulo define las entidades de la base de datos relacionadas con los
usuarios del sistema, sus sesiones (tokens de acceso) y el registro de
auditoría de sus acciones dentro de la API.
"""

from app import db


class Usuario(db.Model):
    """Representa un usuario autenticable en el sistema.

    Attributes:
        id (int): Identificador único primario.
        nombre (str): Nombre de usuario único para inicio de sesión.
        rol (str): Rol asignado (e.g., 'DUEÑO', 'CAJA', 'COCINA', 'OPERADOR').
        activo (bool): Estado del usuario. False indica que está bloqueado.
        tokens (list of TokenAcceso): Colección de tokens de dispositivos asociados.
        acciones (list of Auditoria): Historial de acciones del usuario.
    """

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    rol = db.Column(db.String(20), default='OPERADOR')
    activo = db.Column(db.Boolean, default=True)

    # Relaciones con borrado en cascada configurado correctamente
    tokens = db.relationship(
        'TokenAcceso',
        backref='usuario',
        cascade="all, delete-orphan"
    )
    acciones = db.relationship('Auditoria', backref='usuario')

    def __repr__(self) -> str:
        """Retorna una representación en cadena del usuario.

        Returns:
            str: Cadena formateada con el nombre y rol del usuario.
        """
        return f"<Usuario {self.nombre} (Rol: {self.rol})>"


class TokenAcceso(db.Model):
    """Almacena los tokens de sesión vinculados a dispositivos específicos.

    Attributes:
        id (int): Identificador único primario.
        token (str): Hash o cadena única del token de acceso.
        dispositivo (str): Descripción del dispositivo (e.g., 'Celular Juan').
        usuario_id (int): ID del usuario propietario. Permite nulos temporalmente.
        activo (bool): Estado del token. False si fue revocado o expirado.
        fecha_creacion (datetime): Fecha y hora UTC del registro del token.
    """

    __tablename__ = 'tokens_acceso'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    dispositivo = db.Column(db.String(50))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    # Campo booleano para control de estado desde el servicio
    activo = db.Column(db.Boolean, default=True, nullable=False)

    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        """Retorna una representation en cadena del token.

        Returns:
            str: Cadena formateada con el ID del token y su estado de actividad.
        """
        return f"<TokenAcceso ID: {self.id} - Activo: {self.activo}>"


class Auditoria(db.Model):
    """Registra de forma persistente las acciones críticas de los usuarios.

    Attributes:
        id (int): Identificador único del log.
        usuario_id (int): ID del usuario que ejecutó la acción.
        accion (str): Tipo de operación (e.g., 'CREAR', 'EDITAR').
        tabla_afectada (str): Nombre de la tabla modificada en la base de datos.
        registro_id (int): ID del registro afectado en dicha tabla.
        fecha_hora (datetime): Fecha y hora UTC del evento.
    """

    __tablename__ = 'auditoria'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50))
    tabla_afectada = db.Column(db.String(50))
    registro_id = db.Column(db.Integer)

    # CORRECCIÓN: Se usa la función del motor SQL para consistencia temporal
    fecha_hora = db.Column(db.DateTime, default=db.func.current_timestamp())
