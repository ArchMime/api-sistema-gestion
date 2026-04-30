import os
import uuid
from flask import current_app
from app.models import db, Configuracion, Auditoria, Usuario
from sqlalchemy.exc import SQLAlchemyError

class ConfigService:

    @staticmethod
    def obtener_configuracion():
        """Retorna la configuración actual. Disponible para todos (PWA y Panel)."""
        try:
            config = Configuracion.query.get(1)
            if not config:
                # Si no existe, se crea la primera vez con valores base
                config = Configuracion(id=1)
                db.session.add(config)
                db.session.commit()
            
            return {
                "nombre_local": config.nombre_local,
                "leyenda_header": config.leyenda_header,
                "logo": config.logo_filename,
                "color_principal": config.color_principal,
                "color_secundario": config.color_secundario,
                "moneda": config.moneda_simbolo,
                "tipo_fuente": config.tipo_fuente,
                "tamanno_fuente": config.tamanno_fuente
            }, 200
        except Exception as e:
            return {"error": "Error al cargar configuración", "detalle": str(e)}, 500

    @staticmethod
    def actualizar_configuracion(id_usuario, datos, archivo_logo=None):
        """
        Solo permite modificaciones si el usuario tiene rol 'ADMIN'.
        Pensado para ser usado desde el Panel de Gestión en la laptop servidor.
        """
        try:
            # 1. VALIDACIÓN DE RANGO: Solo el ADMINISTRADOR puede cambiar esto
            admin = Usuario.query.get(id_usuario)
            if not admin or admin.rol != 'ADMIN':
                return {"error": "Acceso denegado: Se requieren permisos de ADMINISTRADOR"}, 403

            config = Configuracion.query.get(1)
            if not config:
                config = Configuracion(id=1)
                db.session.add(config)

            # 2. ACTUALIZAR CAMPOS DE TEXTO
            config.nombre_local = datos.get('nombre_local', config.nombre_local)
            config.leyenda_header = datos.get('leyenda_header', config.leyenda_header)
            config.color_principal = datos.get('color_principal', config.color_principal)
            config.color_secundario = datos.get('color_secundario', config.color_secundario)
            config.moneda_simbolo = datos.get('moneda_simbolo', config.moneda_simbolo)
            config.tipo_fuente = datos.get('tipo_fuente', config.tipo_fuente)
            config.tamanno_fuente = datos.get('tamanno_fuente', config.tamanno_fuente)

            # 3. PROCESAR LOGO (si se adjunta archivo)
            if archivo_logo and archivo_logo.filename != '':
                filename = ConfigService.guardar_logo_fisico(archivo_logo)
                if filename:
                    config.logo_filename = filename

            # 4. REGISTRO EN AUDITORÍA
            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="CAMBIO_CONFIGURACION_SISTEMA",
                tabla_afectada="configuracion",
                registro_id=1
            ))

            db.session.commit()
            return {"status": "ok", "mensaje": "Cambios aplicados correctamente"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos", "detalle": str(e)}, 500

    @staticmethod
    def guardar_logo_fisico(archivo):
        """Guarda la imagen en la carpeta static y retorna el nombre único."""
        try:
            extension = os.path.splitext(archivo.filename).lower()
            if extension not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                return None
            
            # Nombre único para evitar conflictos de caché
            nuevo_nombre = f"logo_{uuid.uuid4().hex[:8]}{extension}"
            base_path = os.path.join(current_app.root_path, 'static', 'img')
            
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            
            archivo.save(os.path.join(base_path, nuevo_nombre))
            return nuevo_nombre
        except Exception:
            return None
