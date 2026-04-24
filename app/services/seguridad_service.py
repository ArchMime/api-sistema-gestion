import uuid
from app.models import db, TokenAcceso, Usuario, Auditoria

class SeguridadService:

    @staticmethod
    def solicitar_acceso(nombre_dispositivo):
        """
        El celular envía su nombre (ej: 'Celular de Persona B').
        Se crea un token temporal en estado 'PENDIENTE'.
        """
        # Generamos un identificador único aleatorio
        token_uuid = str(uuid.uuid4())
        
        nuevo_acceso = TokenAcceso(
            token=token_uuid,
            dispositivo=nombre_dispositivo,
            # Por ahora no tiene usuario_id hasta que el admin lo apruebe
            # Nota: Deberás ajustar el modelo para que usuario_id sea nullable 
            # o manejar un usuario temporal 'PENDIENTE'
        )
        
        db.session.add(nuevo_acceso)
        db.session.commit()
        return token_uuid

    @staticmethod
    def aprobar_acceso(token_recibido, id_usuario_asignado):
        """
        Esta función la ejecutará el panel de Tkinter.
        Vincula el token con un trabajador real (Persona A, B o C).
        """
        acceso = TokenAcceso.query.filter_by(token=token_recibido).first()
        
        if not acceso:
            return {"error": "Token no encontrado"}, 404
            
        acceso.usuario_id = id_usuario_asignado
        
        # Opcional: Registrar en auditoría quién autorizó
        log = Auditoria(
            usuario_id=id_usuario_asignado,
            accion="DISPOSITIVO_AUTORIZADO",
            tabla_afectada="tokens_acceso",
            registro_id=acceso.id
        )
        db.session.add(log)
        db.session.commit()
        return {"status": "Acceso concedido"}, 200

    @staticmethod
    def validar_token(token_a_verificar):
        """
        Se usa en cada petición de la API para saber quién está operando.
        """
        acceso = TokenAcceso.query.filter_by(token=token_a_verificar).first()
        
        if acceso and acceso.usuario_id:
            return acceso.usuario_id # Retorna el ID del trabajador (A, B o C)
        return None
