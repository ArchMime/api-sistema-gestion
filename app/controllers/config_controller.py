from flask import Blueprint, request, jsonify
from app.services.config_service import ConfigService
import traceback

config_bp = Blueprint('configuracion', __name__)

@config_bp.route('/', methods=['GET'])
def obtener_config():
    """
    Endpoint público para obtener la configuración visual.
    """
    try:
        resultado, status = ConfigService.obtener_configuracion()
        return jsonify(resultado), status
    except Exception as e:
        # Log del error para el desarrollador
        print(f"Error en obtener_config: {str(e)}")
        return jsonify({"error": "Error interno al obtener la configuración"}), 500

@config_bp.route('/actualizar', methods=['POST'])
def actualizar_config():
    """
    Endpoint restringido para el Administrador con blindaje de errores.
    """
    try:
        # 1. Extraer datos y logo según el tipo de petición (JSON o Form)
        archivo_logo = None
        
        if request.is_json:
            datos = request.get_json() or {}
        else:
            datos = request.form.to_dict()
            archivo_logo = request.files.get('logo')

        # 2. Identificar al usuario (Red de seguridad para evitar None.get)
        id_usuario = datos.get('id_usuario')

        if not id_usuario:
            return jsonify({"error": "ID de usuario requerido para auditoría"}), 400

        # 3. Ejecutar el servicio
        # El casting a int() se envuelve en el try por si envían texto en el ID
        resultado, status = ConfigService.actualizar_configuracion(
            id_usuario=int(id_usuario),
            datos=datos,
            archivo_logo=archivo_logo
        )
        
        return jsonify(resultado), status

    except ValueError:
        return jsonify({"error": "El ID de usuario debe ser un número válido"}), 400
    
    except Exception as e:
        # Imprime el error completo en la consola del servidor (laptop) para debugear
        print(f"ERROR CRÍTICO en actualizar_config: {traceback.format_exc()}")
        
        # En controladores, no solemos hacer db.session.rollback() directamente 
        # porque eso ya lo hace el Service, pero aquí protegemos que el 
        # servidor no se caiga (500) ante un dato corrupto inesperado.
        return jsonify({
            "error": "Error inesperado en el servidor",
            "detalle": str(e)
        }), 500

