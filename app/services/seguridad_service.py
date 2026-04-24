import uuid
from app.models import db, TokenAcceso, Usuario, Auditoria

class SeguridadService:

    @staticmethod
    def solicitar_acceso(nombre_dispositivo):
        """El celular solicita entrar. Se crea token sin usuario (NULL)."""
        token_uuid = str(uuid.uuid4())
        nuevo_acceso = TokenAcceso(
            token=token_uuid,
            dispositivo=nombre_dispositivo,
            usuario_id=None  # Estado: PENDIENTE
        )
        db.session.add(nuevo_acceso)
        db.session.commit()
        return token_uuid

    @staticmethod
    def crear_usuario(nombre, rol, admin_id=0):
        """Crea un trabajador y audita quién lo hizo."""
        nuevo_usuario = Usuario(nombre=nombre, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.flush() # Para obtener el ID antes del commit
        
        log = Auditoria(
            usuario_id=admin_id, # ID 0 o ID del Admin
            accion="CREAR_USUARIO",
            tabla_afectada="usuarios",
            registro_id=nuevo_usuario.id
        )
        db.session.add(log)
        db.session.commit()
        return nuevo_usuario

    @staticmethod
    def aprobar_acceso(token_recibido, id_usuario_asignado, admin_id=0):
        """Vincula el token a un usuario y registra la autorización."""
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

    @staticmethod
    def validar_token(token_a_verificar):
        """Valida token, existencia de usuario y que no esté bloqueado."""
        acceso = TokenAcceso.query.filter_by(token=token_a_verificar).first()
        
        if not acceso or not acceso.usuario_id:
            return None # No existe o no ha sido aprobado
            
        usuario = Usuario.query.get(acceso.usuario_id)
        
        # Validamos que el usuario exista y esté ACTIVO
        if usuario and usuario.activo:
            return usuario
            
        return None

    @staticmethod
    def cambiar_estado_usuario(usuario_id, estado=False, admin_id=0):
        """Bloquea o activa un usuario sin borrarlo."""
        usuario = Usuario.query.get(usuario_id)
        if usuario:
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
        return False
