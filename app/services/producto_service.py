from app.models import db, Producto, Categoria, Auditoria
from sqlalchemy.exc import SQLAlchemyError
import logging

class ProductoService:

    # --- GESTIÓN DE CATEGORÍAS ---

    @staticmethod
    def guardar_categoria(id_usuario, datos):
        try:
            id_cat = datos.get('id')
            nombre = datos.get('nombre')
            
            if not nombre:
                return {"error": "El nombre de la categoría es obligatorio"}, 400

            categoria = Categoria.query.get(id_cat) if id_cat else None

            if categoria:
                categoria.nombre = nombre
                accion = "EDITAR_CATEGORIA"
            else:
                categoria = Categoria(nombre=nombre)
                db.session.add(categoria)
                accion = "CREAR_CATEGORIA"

            db.session.flush()

            log = Auditoria(
                usuario_id=id_usuario,
                accion=accion,
                tabla_afectada="categorias",
                registro_id=categoria.id
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "ok", "id": categoria.id}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos al guardar categoría", "detalle": str(e)}, 500
        except Exception as e:
            return {"error": "Error inesperado", "detalle": str(e)}, 500

    @staticmethod
    def eliminar_categoria(id_usuario, id_cat):
        try:
            categoria = Categoria.query.get(id_cat)
            if not categoria:
                return {"error": "Categoría no encontrada"}, 404

            if categoria.productos:
                return {"error": "No se puede eliminar una categoría con productos asociados"}, 400

            db.session.delete(categoria)

            log = Auditoria(
                usuario_id=id_usuario,
                accion="ELIMINAR_CATEGORIA",
                tabla_afectada="categorias",
                registro_id=id_cat
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "eliminada"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "No se pudo eliminar la categoría", "detalle": str(e)}, 500

    # --- GESTIÓN DE PRODUCTOS ---

    @staticmethod
    def crear_o_actualizar_producto(id_usuario, datos):
        try:
            codigo = datos.get('codigo_producto')
            # Validación básica de datos requeridos
            if not datos.get('nombre_producto') or not datos.get('precio_producto'):
                return {"error": "Nombre y precio son obligatorios"}, 400

            producto = Producto.query.get(codigo) if codigo else None

            if producto:
                producto.nombre_producto = datos.get('nombre_producto', producto.nombre_producto)
                producto.precio_producto = datos.get('precio_producto', producto.precio_producto)
                producto.descripcion_producto = datos.get('descripcion_producto', producto.descripcion_producto)
                producto.formato_producto = datos.get('formato_producto', producto.formato_producto)
                producto.categoria_id = datos.get('categoria_id', producto.categoria_id)
                if 'activo' in datos:
                    producto.activo = datos['activo']
                accion = "EDITAR_PRODUCTO"
            else:
                producto = Producto(
                    nombre_producto=datos['nombre_producto'],
                    precio_producto=datos['precio_producto'],
                    descripcion_producto=datos.get('descripcion_producto'),
                    formato_producto=datos.get('formato_producto'),
                    categoria_id=datos['categoria_id'],
                    activo=True
                )
                db.session.add(producto)
                accion = "CREAR_PRODUCTO"

            db.session.flush()

            log = Auditoria(
                usuario_id=id_usuario,
                accion=accion,
                tabla_afectada="productos",
                registro_id=producto.codigo_producto
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "ok", "id": producto.codigo_producto}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos al gestionar producto", "detalle": str(e)}, 500
        except KeyError as e:
            return {"error": f"Falta el campo obligatorio: {str(e)}"}, 400

    @staticmethod
    def set_estado_producto(id_usuario, codigo_producto, estado=False):
        try:
            producto = Producto.query.get(codigo_producto)
            if not producto:
                return {"error": "Producto no encontrado"}, 404

            producto.activo = estado
            accion = "ACTIVAR_PRODUCTO" if estado else "DESACTIVAR_PRODUCTO"

            log = Auditoria(
                usuario_id=id_usuario,
                accion=accion,
                tabla_afectada="productos",
                registro_id=codigo_producto
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "success", "nuevo_estado": estado}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"error": "Error al cambiar el estado del producto"}, 500
