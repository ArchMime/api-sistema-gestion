from flask import Blueprint, request, jsonify
from app.services.producto_service import ProductoService

producto_bp = Blueprint('productos', __name__)

# --- CONSULTAS DE CATÁLOGO ---

@producto_bp.route('/menu', methods=['GET'])
def obtener_menu():
    """Vista para la PWA: solo productos disponibles para la venta."""
    return jsonify(ProductoService.obtener_todo_el_menu()), 200

@producto_bp.route('/catalogo-maestro', methods=['GET'])
def obtener_inventario_completo():
    """Vista para gestión: incluye productos pausados para evitar duplicados."""
    return jsonify(ProductoService.obtener_catalogo_maestro()), 200


# --- ACCIONES OPERATIVAS (TODOS LOS USUARIOS) ---

@producto_bp.route('/gestionar', methods=['POST'])
def gestionar_producto():
    """Crea o edita un producto. Requiere ID del usuario que opera."""
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')

    if not id_usuario:
        return jsonify({"error": "Se requiere el ID del usuario para el registro"}), 400

    try:
        resultado = ProductoService.crear_o_actualizar_producto(id_usuario, datos)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@producto_bp.route('/<int:codigo>/estado', methods=['PATCH'])
def cambiar_disponibilidad(codigo):
    """Activa o pausa un producto (ej: falta de stock o fin de temporada)."""
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    nuevo_estado = datos.get('activo') # True para activar, False para pausar

    if id_usuario is None or nuevo_estado is None:
        return jsonify({"error": "Datos incompletos"}), 400

    resultado, status = ProductoService.set_estado_producto(id_usuario, codigo, nuevo_estado)
    return jsonify(resultado), status


# --- GESTIÓN DE CATEGORÍAS ---

@producto_bp.route('/categorias', methods=['GET', 'POST'])
def gestionar_categorias():
    """Cualquier usuario puede ver o crear nuevas categorías."""
    if request.method == 'GET':
        categorias = ProductoService.obtener_categorias()
        return jsonify([{"id": c.id, "nombre": c.nombre} for c in categorias]), 200
    
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    if not id_usuario:
        return jsonify({"error": "ID usuario requerido"}), 400
        
    resultado = ProductoService.guardar_categoria(id_usuario, datos)
    return jsonify(resultado), 201
