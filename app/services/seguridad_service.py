"""Módulo de Servicios de Seguridad y Gestión de Sesiones.

Este módulo encapsula la lógica de negocio para el control de acceso de
dispositivos, la creación de usuarios, la asignación de tokens JWT mediante
Flask-JWT-Extended y la auditoría interna del sistema local.
"""

import uuid
import logging
from app import db
from app.models import TokenAcceso, Usuario, Auditoria
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token


class SeguridadService:
    """Provee métodos estáticos para administrar la seguridad y accesos del sistema."""

    @staticmethod
    def solicitar_acceso(nombre_dispositivo: str) -> str | None:
        """Registra una solicitud de acceso inicial para un dispositivo sin un usuario asignado.

        Args:
            nombre_dispositivo (str): Nombre o etiqueta que identifica al dispositivo cliente.

        Returns:
            str | None: El token UUID generado en formato de cadena si la operación es
            exitosa; None si ocurre un error de persistencia.
        """
        try:
            token_uuid = str(uuid.uuid4())
            nuevo_acceso = TokenAcceso(token=token_uuid, dispositivo=nombre_dispositivo, usuario_id=None)
            db.session.add(nuevo_acceso)
            db.session.commit()
            return token_uuid
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Error de base de datos al solicitar acceso: %s", str(e))
            return None

    @staticmethod
    def crear_usuario(nombre: str, rol: str, admin_id: int = 1) -> Usuario:
        """Crea un nuevo usuario en el sistema y registra la acción en la auditoría.

        Args:
            nombre (str): Nombre único de inicio de sesión para el nuevo usuario.
            rol (str): Nivel de permisos o área asignada al usuario dentro del sistema.
            admin_id (int): Identificador del usuario que ejecuta la acción. Por defecto 1.

        Returns:
            Usuario: La instancia del modelo Usuario recién creada y almacenada.

        Raises:
            ValueError: Si el nombre de usuario ya está registrado en el sistema.
            RuntimeError: Si ocurre un problema imprevisto en la base de datos.
        """
        try:
            nuevo_usuario = Usuario(nombre=nombre, rol=rol)
            db.session.add(nuevo_usuario)
            db.session.flush()

            log = Auditoria(usuario_id=admin_id, accion="CREAR_USUARIO", tabla_afectada="usuarios", registro_id=nuevo_usuario.id)
            db.session.add(log)
            db.session.commit()
            return nuevo_usuario
        except IntegrityError as e:
            db.session.rollback()
            logging.warning("Intento de duplicación de usuario para '%s': %s", nombre, str(e))
            raise ValueError("El nombre de usuario ya existe") from e
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Error interno al crear usuario: %s", str(e))
            raise RuntimeError("Error interno de la base de datos") from e

    @staticmethod
    def aprobar_acceso(token_recibido: str, id_usuario_asignado: int, admin_id: int = 0) -> str:
        """Vincula un dispositivo al usuario y genera un JWT firmado criptográficamente.

        Args:
            token_recibido (str): El token de acceso original emitido por el dispositivo.
            id_usuario_asignado (int): Identificador del usuario al que se vincula el dispositivo.
            admin_id (int): Identificador del administrador que aprueba la vinculación. Por defecto 0.

        Returns:
            str: El token JWT generado con las propiedades y claims del usuario.

        Raises:
            ValueError: Si el token recibido no es válido o ya se encuentra inactivo.
            RuntimeError: Si la base de datos experimenta fallos de almacenamiento.
        """
        try:
            stmt = db.select(TokenAcceso).filter_by(token=token_recibido, activo=True)
            acceso = db.session.execute(stmt).scalar_one_or_none()

            if not acceso:
                raise ValueError("Token de solicitud no encontrado o inactivo")

            acceso.usuario_id = id_usuario_assigned = id_usuario_asignado

            log = Auditoria(usuario_id=admin_id, accion="AUTORIZAR_DISPOSITIVO", tabla_afectada="tokens_acceso", registro_id=acceso.id)
            db.session.add(log)
            db.session.commit()

            claims = {"rol": acceso.usuario.rol}
            jwt_token = create_access_token(identity=str(acceso.usuario_id), additional_claims=claims)
            return jwt_token
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Error al aprobar acceso y generar JWT: %s", str(e))
            raise RuntimeError("No se pudo procesar la aprobación") from e

    @staticmethod
    def verificar_jti_bloqueado(jti_a_verificar: str) -> bool:
        """Verifica en base de datos si un token específico ha sido revocado o desactivado.

        Args:
            jti_a_verificar (str): El identificador único del JWT extraído del payload.

        Returns:
            bool: True si el token no existe, está inactivo o no tiene un usuario asignado 
            (lo que invalida el JWT); False si continúa activo y autorizado.
        """
        try:
            stmt = db.select(TokenAcceso).filter_by(token=jti_a_verificar)
            acceso = db.session.execute(stmt).scalar_one_or_none()
            if not acceso or not acceso.usuario_id or not acceso.activo:
                return True
            return False
        except SQLAlchemyError:
            return True

    @staticmethod
    def cambiar_estado_usuario(usuario_id: int, estado: bool = False, admin_id: int = 0) -> bool:
        """Modifica el estado de activación de un usuario sin eliminar el registro físico.

        Args:
            usuario_id (int): Identificador del usuario que se desea bloquear o activar.
            estado (bool): Estado final deseado. False para bloquear, True para activar. Por defecto False.
            admin_id (int): Identificador del administrador que ejecuta la acción. Por defecto 0.

        Returns:
            bool: True si el cambio de estado y la auditoría se registran exitosamente.

        Raises:
            ValueError: Si el identificador provisto no coincide con ningún usuario.
            RuntimeError: Si ocurre un problema al guardar los cambios en disco.
        """
        try:
            usuario = db.session.get(Usuario, usuario_id)
            if not usuario:
                raise ValueError("El usuario especificado no existe")

            usuario.activo = estado
            log = Auditoria(usuario_id=admin_id, accion="BLOQUEAR_USUARIO" if not estado else "ACTIVAR_USUARIO", tabla_afectada="usuarios", registro_id=usuario.id)
            db.session.add(log)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Error al cambiar estado de usuario ID %s: %s", usuario_id, str(e))
            raise RuntimeError("Error al procesar el cambio de estado") from e
