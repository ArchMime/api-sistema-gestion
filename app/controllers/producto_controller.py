from flask import Blueprint, request, jsonify
from app.services.producto_service import ProductoService
from app.models.producto import Categoria

producto_bp = Blueprint('productos', __name__)

@producto_bp.route('/menu', methods=['GET'])
def obtener_menu():
    """Retorna el catálogo completo agrupado por categorías."""
    menu = ProductoService.obtener_todo_el_menu()
    return jsonify(menu), 200

@producto_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Lista solo las categorías disponibles (útil para formularios)."""
    categorias = Categoria.query.all()
    resultado = [{"id": c.id, "nombre": c.nombre} for c in categorias]
    return jsonify(resultado), 200

@producto_bp.route('/gestionar', methods=['POST'])
def gestionar_producto():
    """
    Crea o edita un producto.
    JSON esperado: { "id_usuario": 1, "nombre_producto": "Café", "precio_producto": 1500, ... }
    """
    datos = request.get_json()
    
    # Validar que venga el ID del usuario para la auditoría
    id_usuario = datos.get('id_usuario')
    if not id_usuario:
        return jsonify({"error": "Identificación de usuario requerida"}), 400

    try:
        resultado = ProductoService.crear_o_actualizar_producto(id_usuario, datos)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@producto_bp.route('/<int:codigo_producto>', methods=['DELETE'])
def eliminar(codigo_producto):
    """Elimina un producto si no tiene historial de ventas."""
    # En una app real, el id_usuario vendría del token de sesión
    id_usuario = request.args.get('id_usuario') 
    
    if not id_usuario:
        return jsonify({"error": "ID de usuario es necesario para auditoría"}), 400

    resultado, status = ProductoService.eliminar_producto(int(id_usuario), codigo_producto)
    return jsonify(resultado), status
