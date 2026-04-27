from flask import Blueprint, request, jsonify
from app.services.caja_service import CajaService

caja_bp = Blueprint('caja', __name__)

@caja_bp.route('/estado', methods=['GET'])
def consultar_estado():
    """
    Verifica el estado actual de la caja.
    Retorna si está LIBRE, BLOQUEADO (abierta) o EXISTENTE (cerrada pero de hoy).
    """
    resultado, status = CajaService.verificar_estado_diario()
    return jsonify(resultado), status

@caja_bp.route('/abrir', methods=['POST'])
def abrir():
    """Apertura de caja con lógica de forzado opcional."""
    datos = request.get_json()
    # id_usuario vendría del token en una implementación real
    resultado, status = CajaService.abrir_caja(
        id_usuario=datos.get('id_usuario'),
        monto_inicial=datos.get('monto_inicial', 0),
        forzar_nueva=datos.get('forzar_nueva', False)
    )
    return jsonify(resultado), status

@caja_bp.route('/reabrir', methods=['POST'])
def reabrir():
    """Reabre una caja cerrada para ajustes."""
    datos = request.get_json()
    resultado, status = CajaService.reabrir_caja(
        id_usuario=datos.get('id_usuario'),
        id_caja=datos.get('id_caja')
    )
    return jsonify(resultado), status

@caja_bp.route('/egreso', methods=['POST'])
def registrar_egreso():
    """Registro de gastos vinculado a la caja activa."""
    datos = request.get_json()
    resultado, status = CajaService.registrar_egreso(
        id_usuario=datos.get('id_usuario'),
        monto=datos.get('monto'),
        descripcion=datos.get('descripcion'),
        categoria=datos.get('categoria', 'VARIOS')
    )
    return jsonify(resultado), status

@caja_bp.route('/cerrar', methods=['POST'])
def cerrar():
    """Cierre de caja con cuadratura automática."""
    datos = request.get_json()
    resultado, status = CajaService.cerrar_caja(
        id_usuario=datos.get('id_usuario'),
        efectivo_fisico=datos.get('efectivo_fisico'),
        observaciones=datos.get('observaciones', "")
    )
    return jsonify(resultado), status

@caja_bp.route('/historial', methods=['GET'])
def listar_historial():
    """Lista todas las cajas para el panel de informes del administrador."""
    resultado, status = CajaService.listar_cajas_admin()
    return jsonify(resultado), status
