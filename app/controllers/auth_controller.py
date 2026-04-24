from flask import Blueprint, request, jsonify
from app.services.seguridad_service import SeguridadService
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/solicitar-acceso', methods=['POST'])
def solicitar():
    """
    Punto de entrada para dispositivos nuevos.
    JSON: { "nombre_dispositivo": "Xiaomi de Persona C" }
    """
    datos = request.get_json()
    nombre_dispositivo = datos.get('nombre_dispositivo', 'Dispositivo Desconocido')
    
    # Genera el token UUID en estado pendiente
    token = SeguridadService.solicitar_acceso(nombre_dispositivo)
    
    return jsonify({
        "token": token,
        "mensaje": "Solicitud enviada. Espere aprobación en el panel del local."
    }), 202

@auth_bp.route('/validar-token', methods=['POST'])
def validar():
    """
    El celular usa esto cada vez que abre la app para saber si ya lo aprobaron.
    """
    datos = request.get_json()
    token = datos.get('token')
    
    if not token:
        return jsonify({"error": "Token requerido"}), 400
        
    usuario_id = SeguridadService.validar_token(token)
    
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)
        return jsonify({
            "status": "APROBADO",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "rol": usuario.rol
            }
        }), 200
    else:
        return jsonify({"status": "PENDIENTE_O_REVOCADO"}), 401

@auth_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Útil para que el panel de Tkinter sepa a quién asignar un token."""
    usuarios = Usuario.query.all()
    return jsonify([{"id": u.id, "nombre": u.nombre} for u in usuarios]), 200
