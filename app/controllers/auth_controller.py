from flask import Blueprint, request, jsonify
from app.services.seguridad_service import SeguridadService

auth_bp = Blueprint('auth', __name__)

# --- RUTAS PARA EL CELULAR (PWA) ---

@auth_bp.route('/solicitar-acceso', methods=['POST'])
def solicitar():
    datos = request.get_json()
    nombre_dispositivo = datos.get('nombre_dispositivo')
    
    if not nombre_dispositivo:
        return jsonify({"error": "Falta el nombre del dispositivo"}), 400
        
    token = SeguridadService.solicitar_acceso(nombre_dispositivo)
    return jsonify({
        "token": token,
        "mensaje": "Solicitud enviada. Pida al administrador que autorice este equipo."
    }), 202

@auth_bp.route('/validar-token', methods=['POST'])
def validar():
    datos = request.get_json()
    token = datos.get('token')
    
    if not token:
        return jsonify({"error": "Token requerido"}), 400
        
    usuario = SeguridadService.validar_token(token)
    
    if usuario:
        return jsonify({
            "status": "APROBADO",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "rol": usuario.rol
            }
        }), 200
    
    # Si no devuelve usuario, puede estar pendiente o el usuario ser inactivo
    return jsonify({"status": "PENDIENTE_O_BLOQUEADO"}), 401


# --- RUTAS EXCLUSIVAS PARA EL PANEL DE GESTIÓN (TKINTER / ADMIN) ---

@auth_bp.route('/admin/aprobar-acceso', methods=['POST'])
def aprobar():
    datos = request.get_json()
    token_uuid = datos.get('token')
    usuario_id = datos.get('usuario_id')
    admin_id = datos.get('admin_id', 0) # Por defecto Admin Sistema
    
    if not token_uuid or not usuario_id:
        return jsonify({"error": "Datos incompletos"}), 400
        
    resultado, status_code = SeguridadService.aprobar_acceso(token_uuid, usuario_id, admin_id)
    return jsonify(resultado), status_code

@auth_bp.route('/admin/usuarios', methods=['POST'])
def crear_usuario():
    datos = request.get_json()
    nombre = datos.get('nombre')
    rol = datos.get('rol')
    admin_id = datos.get('admin_id', 0)
    
    if not nombre or not rol:
        return jsonify({"error": "Nombre y rol son requeridos"}), 400
        
    nuevo_u = SeguridadService.crear_usuario(nombre, rol, admin_id)
    return jsonify({"id": nuevo_u.id, "nombre": nuevo_u.nombre, "rol": nuevo_u.rol}), 201

@auth_bp.route('/admin/usuarios/<int:id>/estado', methods=['PATCH'])
def cambiar_estado(id):
    datos = request.get_json()
    nuevo_estado = datos.get('activo') # True o False
    admin_id = datos.get('admin_id', 0)
    
    exito = SeguridadService.cambiar_estado_usuario(id, nuevo_estado, admin_id)
    if exito:
        return jsonify({"mensaje": "Estado actualizado correctamente"}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404
