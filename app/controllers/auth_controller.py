"""Módulo de Controladores para la Autenticación y Gestión de Accesos.

Este módulo define los endpoints de la API (Blueprint) encargados de recibir
las solicitudes de acceso de los dispositivos, delegar la lógica al servicio
de seguridad y administrar las credenciales de usuarios mediante JWT.
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.seguridad_service import SeguridadService

auth_bp = Blueprint('auth', __name__)


# --- RUTAS PARA DISPOSITIVOS CLIENTES (PWA) ---

@auth_bp.route('/solicitar-acceso', methods=['POST'])
def solicitar() -> tuple[Response, int]:
    """Registra una petición inicial de acceso para un dispositivo local.

    Returns:
        tuple: Un objeto Response con el token UUID y un mensaje explicativo junto
        con el código de estado HTTP 202 (Accepted); o un JSON de error con su
        respectivo código HTTP (400 o 500).
    """
    datos = request.get_json() or {}
    nombre_dispositivo = datos.get('nombre_dispositivo')

    if not nombre_dispositivo:
        return jsonify({"error": "Falta el nombre del dispositivo"}), 400

    token = SeguridadService.solicitar_acceso(nombre_dispositivo)

    if not token:
        return jsonify({"error": "No se pudo procesar la solicitud en la base de datos"}), 500

    return jsonify({
        "token": token,
        "mensaje": "Solicitud enviada. Pida al administrador que autorice este equipo."
    }), 202


@auth_bp.route('/verificar-sesion', methods=['GET'])
@jwt_required()
def verificar_sesion() -> tuple[Response, int]:
    """Verifica de forma ligera si el token JWT actual de la PWA sigue vigente.

    Gracias a Flask-JWT-Extended, si el flujo llega al cuerpo de esta función, significa
    que el token estructuralmente es válido y pasó el filtro del blocklist de la base de datos.

    Returns:
        tuple: Un objeto Response con el estado de aprobación y el identificador de usuario 
        junto con el código HTTP 200.
    """
    usuario_id = get_jwt_identity()
    return jsonify({
        "status": "APROBADO",
        "usuario_id": usuario_id
    }), 200


# --- RUTAS EXCLUSIVAS PARA ADMINISTRACIÓN (PROTEGIDAS POR JWT) ---

@auth_bp.route('/admin/aprobar-acceso', methods=['POST'])
@jwt_required()
def aprobar() -> tuple[Response, int]:
    """Vincula un token UUID de dispositivo a un usuario y genera un JWT de acceso.

    Extrae el identificador del administrador directamente desde la sesión criptográfica cifrada.

    Returns:
        tuple: Un objeto Response con la cadena JWT firmada y el código HTTP 200; o
        un JSON con la descripción del fallo y el código de estado HTTP (400 o 500).
    """
    admin_id = get_jwt_identity()
    datos = request.get_json() or {}
    token_uuid = datos.get('token')
    usuario_id = datos.get('usuario_id')

    if not token_uuid or not usuario_id:
        return jsonify({"error": "Datos de aprobación incompletos"}), 400

    try:
        jwt_token = SeguridadService.aprobar_acceso(token_uuid, int(usuario_id), int(admin_id))
        return jsonify({
            "status": "Acceso concedido",
            "access_token": jwt_token
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/admin/usuarios', methods=['POST'])
@jwt_required()
def crear_usuario() -> tuple[Response, int]:
    """Crea un nuevo usuario en la base de datos local y audita la acción.

    Returns:
        tuple: Un objeto Response con el ID, nombre y rol del registro creado junto con 
        el código HTTP 201 (Created); o un JSON de error con su código HTTP pertinente.
    """
    admin_id = get_jwt_identity()
    datos = request.get_json() or {}
    nombre = datos.get('nombre')
    rol = datos.get('rol')

    if not nombre or not rol:
        return jsonify({"error": "Nombre y rol son campos obligatorios"}), 400

    try:
        nuevo_usuario = SeguridadService.crear_usuario(nombre, rol, int(admin_id))
        return jsonify({
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "rol": nuevo_usuario.rol
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/admin/usuarios/<int:id>/estado', methods=['PATCH'])
@jwt_required()
def cambiar_estado(id: int) -> tuple[Response, int]:
    """Modifica el estado físico activo/bloqueado de un usuario específico del sistema.

    Args:
        id (int): Identificador numérico primario del usuario a alterar.

    Returns:
        tuple: Un objeto Response con la confirmación de la actualización y código HTTP 200;
        o un JSON con el mensaje de error estructurado y el código HTTP correspondiente.
    """
    admin_id = get_jwt_identity()
    datos = request.get_json() or {}
    nuevo_estado = datos.get('activo')

    if nuevo_estado is None:
        return jsonify({"error": "Falta el campo booleano 'activo' en la petición"}), 400

    try:
        SeguridadService.cambiar_estado_usuario(id, bool(nuevo_estado), int(admin_id))
        return jsonify({"mensaje": "Estado de usuario actualizado correctamente"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
