from flask import Blueprint, request, jsonify
from app.services.caja_service import CajaService
from app.models.caja import Caja
from datetime import datetime

caja_bp = Blueprint('caja', __name__)

@caja_bp.route('/estado', methods=['GET'])
def consultar_estado():
    """Verifica si la caja de hoy está abierta y devuelve el resumen actual."""
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    caja = Caja.query.filter_by(fecha=fecha_hoy).first()
    
    if not caja:
        return jsonify({"estado": "NO_INICIADA"}), 200
        
    return jsonify({
        "id_caja": caja.id_caja,
        "estado": caja.estado_caja,
        "saldo_inicial": caja.saldo_inicial,
        "fecha": caja.fecha
    }), 200

@caja_bp.route('/abrir', methods=['POST'])
def abrir():
    """Apertura de caja diaria."""
    datos = request.get_json()
    # id_usuario es obligatorio para saber quién abrió
    resultado, status = CajaService.abrir_caja(
        id_usuario=datos.get('id_usuario'),
        monto_inicial=datos.get('monto_inicial', 0)
    )
    return jsonify(resultado), status

@caja_bp.route('/egreso', methods=['POST'])
def registrar_egreso():
    """Registro de gastos (pan, gas, propinas, etc.)."""
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
    """Cierre de caja con cuadratura."""
    datos = request.get_json()
    resultado, status = CajaService.cerrar_caja(
        id_usuario=datos.get('id_usuario'),
        efectivo_fisico=datos.get('efectivo_fisico'),
        observaciones=datos.get('observaciones', "")
    )
    return jsonify(resultado), status

@caja_bp.route('/corregir', methods=['PUT'])
def corregir():
    """Corrección de error humano en el conteo final."""
    datos = request.get_json()
    resultado, status = CajaService.corregir_cierre_caja(
        id_usuario=datos.get('id_usuario'),
        id_caja=datos.get('id_caja'),
        nuevo_efectivo_fisico=datos.get('nuevo_efectivo_fisico'),
        motivo=datos.get('motivo')
    )
    return jsonify(resultado), status
