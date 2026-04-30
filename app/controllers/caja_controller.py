from flask import Blueprint, request, jsonify
from app.services.caja_service import CajaService

caja_bp = Blueprint('caja', __name__)

@caja_bp.route('/estado', methods=['GET'])
def consultar_estado():
    # Solo pasamos la respuesta del service blindado
    resultado, status = CajaService.verificar_estado_diario()
    return jsonify(resultado), status

@caja_bp.route('/abrir', methods=['POST'])
def abrir():
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    monto_inicial = datos.get('monto_inicial')

    if id_usuario is None or monto_inicial is None:
        return jsonify({"error": "Falta id_usuario o monto_inicial"}), 400

    resultado, status = CajaService.abrir_caja(
        id_usuario=id_usuario,
        monto_inicial=monto_inicial,
        forzar_nueva=datos.get('forzar_nueva', False)
    )
    return jsonify(resultado), status

@caja_bp.route('/reabrir', methods=['POST'])
def reabrir():
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    id_caja = datos.get('id_caja')

    if not id_usuario or not id_caja:
        return jsonify({"error": "ID de usuario y de caja son requeridos"}), 400

    resultado, status = CajaService.reabrir_caja(id_usuario, id_caja)
    return jsonify(resultado), status

@caja_bp.route('/egreso', methods=['POST'])
def registrar_egreso():
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    monto = datos.get('monto')

    if not id_usuario or not monto:
        return jsonify({"error": "Datos de egreso incompletos"}), 400

    resultado, status = CajaService.registrar_egreso(
        id_usuario=id_usuario,
        monto=monto,
        descripcion=datos.get('descripcion', "Sin descripción"),
        categoria=datos.get('categoria', 'VARIOS')
    )
    return jsonify(resultado), status

@caja_bp.route('/cerrar', methods=['POST'])
def cerrar():
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    efectivo_fisico = datos.get('efectivo_fisico')

    if id_usuario is None or efectivo_fisico is None:
        return jsonify({"error": "Falta id_usuario o efectivo_fisico para cerrar"}), 400

    resultado, status = CajaService.cerrar_caja(
        id_usuario=id_usuario,
        efectivo_fisico=efectivo_fisico,
        observaciones=datos.get('observaciones', "")
    )
    return jsonify(resultado), status

@caja_bp.route('/historial', methods=['GET'])
def listar_historial():
    # Ideal para el Panel Admin
    resultado, status = CajaService.listar_cajas_admin()
    return jsonify(resultado), status
