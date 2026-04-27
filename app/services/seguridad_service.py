import uuid
import logging
from app.models import db, TokenAcceso, Usuario, Auditoria
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class SeguridadService:

    @staticmethod
    def solicitar_acceso(nombre_dispositivo):
        """El celular solicita entrar. Se crea token sin usuario (NULL)."""
        try:
            token_uuid = str(uuid.uuid4())
            nuevo_acceso = TokenAcceso(
                token=token_uuid,
                dispositivo=nombre_dispositivo,
                usuario_id=None
            )
            db.session.add(nuevo_acceso)
            db.session.commit()
            return token_uuid
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al solicitar acceso: {str(e)}")
            return None

    @staticmethod
    def crear_usuario(nombre, rol, admin_id=0):
        """Crea un trabajador y audita quién lo hizo con protección de duplicados."""
        try:
            nuevo_usuario = Usuario(nombre=nombre, rol=rol)
            db.session.add(nuevo_usuario)
            db.session.flush()

            log = Auditoria(
                usuario_id=admin_id,
                accion="CREAR_USUARIO",
                tabla_afectada="usuarios",
                registro_id=nuevo_usuario.id
            )
            db.session.add(log)
            db.session.commit()
            return nuevo_usuario
        except IntegrityError:
            db.session.rollback()
            return {"error": "El nombre de usuario ya existe"}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error interno del servidor"}, 500

    @staticmethod
    def aprobar_acceso(token_recibido, id_usuario_asignado, admin_id=0):
        """Vincula el token a un usuario y registra la autorización."""
        try:
            acceso = TokenAcceso.query.filter_by(token=token_recibido).first()
            if not acceso:
                return {"error": "Token no encontrado"}, 404

            acceso.usuario_id = id_usuario_asignado

            log = Auditoria(
                usuario_id=admin_id,
                accion="AUTORIZAR_DISPOSITIVO",
                tabla_afectada="tokens_acceso",
                registro_id=acceso.id
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "Acceso concedido"}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"error": "No se pudo aprobar el acceso"}, 500

    @staticmethod
    def validar_token(token_a_verificar):
        """Valida token de forma segura (solo lectura)."""
        try:
            acceso = TokenAcceso.query.filter_by(token=token_a_verificar).first()
            if not acceso or not acceso.usuario_id:
                return None

            usuario = Usuario.query.get(acceso.usuario_id)
            if usuario and usuario.activo:
                return usuario
            return None
        except SQLAlchemyError:
            return None # En validación, si falla la DB, simplemente no entra

    @staticmethod
    def cambiar_estado_usuario(usuario_id, estado=False, admin_id=0):
        """Bloquea o activa un usuario sin borrarlo."""
        try:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return False
            
            usuario.activo = estado
            log = Auditoria(
                usuario_id=admin_id,
                accion="BLOQUEAR_USUARIO" if not estado else "ACTIVAR_USUARIO",
                tabla_afectada="usuarios",
                registro_id=usuario.id
            )
            db.session.add(log)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False
