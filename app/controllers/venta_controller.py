from flask import Blueprint, request, jsonify
from app.services.venta_service import VentaService
from app.models.venta import Venta

venta_bp = Blueprint('venta', __name__)

@venta_bp.route('/', methods=['POST'])
def gestionar_pedido():
    """
    Crea una venta o añade productos a una existente (Mesa abierta).
    Espera: { "id_usuario": 1, "id_venta": null, "productos": [...], "cliente": "Mesa 5" }
    """
    datos = request.get_json()

    # Validamos datos mínimos para operar
    if not datos or not datos.get('id_usuario') or not datos.get('productos'):
        return jsonify({"error": "Faltan datos obligatorios (usuario o productos)"}), 400

    resultado, status = VentaService.gestionar_venta(
        id_usuario=datos.get('id_usuario'),
        id_venta=datos.get('id_venta'), # Si es None, el Service crea una nueva
        cliente=datos.get('cliente', "Consumo Local"),
        productos=datos.get('productos', []),
        estado=datos.get('estado', 'PENDIENTE')
    )
    return jsonify(resultado), status

@venta_bp.route('/pagar', methods=['POST'])
def procesar_pago():
    """
    Finaliza la venta y la vincula al arqueo de caja.
    Espera: { "id_usuario": 1, "id_venta": 10, "forma_pago": "EFECTIVO", "propina": 500 }
    """
    datos = request.get_json()

    if not datos or not datos.get('id_venta') or not datos.get('forma_pago'):
        return jsonify({"error": "ID de venta y forma de pago son requeridos"}), 400

    resultado, status = VentaService.finalizar_pago(
        id_usuario=datos.get('id_usuario'),
        id_venta=datos.get('id_venta'),
        forma_pago=datos.get('forma_pago'),
        propina=datos.get('propina', 0)
    )
    return jsonify(resultado), status

@venta_bp.route('/<int:id_venta>/anular', methods=['PATCH'])
def anular_pedido(id_venta):
    """
    Invalida una cuenta abierta que no será procesada.
    Espera: { "id_usuario": 1, "motivo": "Cliente se retiró" }
    """
    datos = request.get_json()
    id_usuario = datos.get('id_usuario') if datos else None
    
    if not id_usuario:
        return jsonify({"error": "ID de usuario requerido para auditoría"}), 400

    resultado, status = VentaService.anular_venta(
        id_usuario=id_usuario,
        id_venta=id_venta,
        motivo=datos.get('motivo', "Anulación manual")
    )
    return jsonify(resultado), status

@venta_bp.route('/', methods=['GET'])
def listar_ventas():
    """
    Lista ventas con filtros. Útil para ver mesas abiertas o historial.
    Ejemplo: /api/ventas/?estado=PENDIENTE
    """
    estado = request.args.get('estado')
    fecha = request.args.get('fecha')

    query = Venta.query

    if estado:
        query = query.filter_by(estado_pago=estado)
    if fecha:
        query = query.filter_by(fecha_venta=fecha)

    ventas = query.order_by(Venta.id_venta.desc()).all()

    return jsonify([{
        "id_venta": v.id_venta,
        "cliente": v.cliente,
        "total": v.total,
        "estado": v.estado_pago,
        "fecha": v.fecha_venta,
        "hora": v.hora_venta
    } for v in ventas]), 200

@venta_bp.route('/<int:id_venta>', methods=['GET'])
def ver_detalle(id_venta):
    """
    Retorna la información completa de la venta con sus productos.
    Usa el precio histórico guardado en el detalle.
    """
    v = Venta.query.get(id_venta)
    if not v:
        return jsonify({"error": "Venta no encontrada"}), 404

    return jsonify({
        "id_venta": v.id_venta,
        "cliente": v.cliente,
        "total": v.total,
        "estado": v.estado_pago,
        "fecha": v.fecha_venta,
        "hora": v.hora_venta,
        "forma_pago": v.forma_pago,
        "propina": v.propina,
        "detalle_productos": [{
            "id_producto": p.id_producto_fk,
            "nombre": p.producto.nombre_producto,
            "cantidad": p.cantidad,
            "precio_unitario": p.precio_unitario,
            "subtotal": p.subtotal
        } for p in v.detalles]
    }), 200
