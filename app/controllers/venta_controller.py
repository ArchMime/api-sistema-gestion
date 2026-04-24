from flask import Blueprint, request, jsonify
from app.models.venta import Venta
from datetime import datetime

# ESTA LÍNEA ES LA QUE FALTABA:
venta_bp = Blueprint('venta_bp', __name__)

@venta_bp.route('/', methods=['GET'])
def listar_ventas():
    estado = request.args.get('estado') 
    fecha = request.args.get('fecha')   
    
    query = Venta.query

    if estado:
        query = query.filter_by(estado_pago=estado)
    
    if fecha:
        query = query.filter_by(fecha_venta=fecha)
    else:
        hoy = datetime.now().strftime("%d-%m-%Y")
        query = query.filter_by(fecha_venta=hoy)

    ventas = query.all()
    
    resultado = [{
        "id_venta": v.id_venta,
        "cliente": v.cliente,
        "total": v.total,
        "estado": v.estado_pago,
        "hora": v.hora_venta,
        "forma_pago": v.forma_pago
    } for v in ventas]
    
    return jsonify(resultado), 200

@venta_bp.route('/historial/mes', methods=['GET'])
def historial_mensual():
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    
    if not mes or not anio:
        return jsonify({"error": "Faltan mes y anio"}), 400
        
    filtro_fecha = f"%-{mes}-{anio}"
    ventas = Venta.query.filter(Venta.fecha_venta.like(filtro_fecha)).all()
    
    return jsonify([v.id_venta for v in ventas]), 200
