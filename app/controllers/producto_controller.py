from flask import Blueprint, request, jsonify
from app.services.producto_service import ProductoService

producto_bp = Blueprint('productos', __name__)

# --- CONSULTAS DE CATÁLOGO ---

@producto_bp.route('/menu', methods=['GET'])
def obtener_menu():
    # La PWA necesita esto rápido y limpio
    return jsonify(ProductoService.obtener_todo_el_menu()), 200

@producto_bp.route('/catalogo-maestro', methods=['GET'])
def obtener_inventario_completo():
    return jsonify(ProductoService.obtener_catalogo_maestro()), 200


# --- ACCIONES OPERATIVAS ---

@producto_bp.route('/gestionar', methods=['POST'])
def gestionar_producto():
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')

    if not id_usuario:
        return jsonify({"error": "Se requiere el ID del usuario para el registro"}), 400

    # Ahora recibimos la tupla directamente del Service blindado
    resultado, status = ProductoService.crear_o_actualizar_producto(id_usuario, datos)
    return jsonify(resultado), status

@producto_bp.route('/<int:codigo>/estado', methods=['PATCH'])
def cambiar_disponibilidad(codigo):
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    nuevo_estado = datos.get('activo') 

    if id_usuario is None or nuevo_estado is None:
        return jsonify({"error": "Datos incompletos"}), 400

    resultado, status = ProductoService.set_estado_producto(id_usuario, codigo, nuevo_estado)
    return jsonify(resultado), status


# --- GESTIÓN DE CATEGORÍAS ---

@producto_bp.route('/categorias', methods=['GET', 'POST'])
def gestionar_categorias():
    if request.method == 'GET':
        categorias = ProductoService.obtener_categorias()
        return jsonify([{"id": c.id, "nombre": c.nombre} for c in categorias]), 200

    # Para el POST (Crear/Editar)
    datos = request.get_json()
    id_usuario = datos.get('id_usuario')
    if not id_usuario:
        return jsonify({"error": "ID usuario requerido"}), 400

    resultado, status = ProductoService.guardar_categoria(id_usuario, datos)
    return jsonify(resultado), status

@producto_bp.route('/categorias/<int:id_cat>', methods=['DELETE'])
def borrar_categoria(id_cat):
    id_usuario = request.args.get('id_usuario') # O del JSON
    if not id_usuario:
        return jsonify({"error": "ID usuario requerido"}), 400
        
    resultado, status = ProductoService.eliminar_categoria(id_usuario, id_cat)
    return jsonify(resultado), status
