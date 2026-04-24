from flask import Blueprint, request, jsonify
from app.models.venta import Venta
from datetime import datetime

# ... (los otros imports y el blueprint se mantienen)

@venta_bp.route('/', methods=['GET'])
def listar_ventas():
    """
    Lista ventas con filtros opcionales por URL:
    /api/ventas/?estado=PAGADO
    /api/ventas/?fecha=24-04-2026
    """
    estado = request.args.get('estado') # PENDIENTE o PAGADO
    fecha = request.args.get('fecha')   # dd-mm-aaaa
    
    query = Venta.query

    if estado:
        query = query.filter_by(estado_pago=estado)
    
    if fecha:
        query = query.filter_by(fecha_venta=fecha)
    else:
        # Por defecto, si no pide fecha, mostramos lo de hoy
        hoy = datetime.now().strftime("%d-%m-%Y")
        query = query.filter_by(fecha_venta=hoy)

    ventas = query.all()
    
    resultado = []
    for v in ventas:
        resultado.append({
            "id_venta": v.id_venta,
            "cliente": v.cliente,
            "total": v.total,
            "estado": v.estado_pago,
            "hora": v.hora_venta,
            "forma_pago": v.forma_pago
        })
    return jsonify(resultado), 200

@venta_bp.route('/historial/mes', methods=['GET'])
def historial_mensual():
    """
    Filtra por mes y año: /api/ventas/historial/mes?mes=04&anio=2026
    """
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    
    if not mes or not anio:
        return jsonify({"error": "Faltan mes y anio"}), 400
        
    # Usamos LIKE para buscar fechas que terminen en '-mes-anio'
    filtro_fecha = f"%-{mes}-{anio}"
    ventas = Venta.query.filter(Venta.fecha_venta.like(filtro_fecha)).all()
    
    # ... (formatear resultado similar al anterior)
    return jsonify([v.id_venta for v in ventas]), 200 # Ejemplo simplificado
