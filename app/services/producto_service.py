from app.models import db, Producto, Categoria, Auditoria

class ProductoService:

    @staticmethod
    def obtener_todo_el_menu():
        """
        Devuelve todos los productos agrupados por su categoría.
        Ideal para construir la interfaz de la PWA de forma organizada.
        """
        categorias = Categoria.query.all()
        menu = []
        
        for cat in categorias:
            items = []
            for p in cat.productos:
                items.append({
                    "id": p.codigo_producto,
                    "nombre": p.nombre_producto,
                    "precio": p.precio_producto,
                    "formato": p.formato_producto,
                    "descripcion": p.descripcion_producto
                })
            
            menu.append({
                "categoria": cat.nombre,
                "productos": items
            })
            
        return menu

    @staticmethod
    def crear_o_actualizar_producto(id_usuario, datos):
        """
        Permite agregar nuevos productos o editar precios/nombres.
        'datos' es un diccionario con la info del producto.
        """
        codigo = datos.get('codigo_producto')
        producto = Producto.query.get(codigo) if codigo else None

        if producto:
            # Editamos el existente
            producto.nombre_producto = datos.get('nombre_producto', producto.nombre_producto)
            producto.precio_producto = datos.get('precio_producto', producto.precio_producto)
            producto.descripcion_producto = datos.get('descripcion_producto', producto.descripcion_producto)
            producto.formato_producto = datos.get('formato_producto', producto.formato_producto)
            producto.categoria_id = datos.get('categoria_id', producto.categoria_id)
            accion = "EDITAR_PRODUCTO"
        else:
            # Creamos uno nuevo
            producto = Producto(
                nombre_producto=datos['nombre_producto'],
                precio_producto=datos['precio_producto'],
                descripcion_producto=datos.get('descripcion_producto'),
                formato_producto=datos.get('formato_producto'),
                categoria_id=datos['categoria_id']
            )
            db.session.add(producto)
            accion = "CREAR_PRODUCTO"

        db.session.flush() # Para obtener el ID si es nuevo

        # Registro de Auditoría
        log = Auditoria(
            usuario_id=id_usuario,
            accion=accion,
            tabla_afectada="productos",
            registro_id=producto.codigo_producto
        )
        db.session.add(log)
        db.session.commit()
        
        return {"status": "ok", "id": producto.codigo_producto}

    @staticmethod
    def eliminar_producto(id_usuario, codigo_producto):
        """
        Intenta eliminar un producto. SQLAlchemy protegerá la integridad
        si el producto ya tiene ventas asociadas (ondelete='RESTRICT').
        """
        producto = Producto.query.get(codigo_producto)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
            
        try:
            db.session.delete(producto)
            log = Auditoria(
                usuario_id=id_usuario,
                accion="ELIMINAR_PRODUCTO",
                tabla_afectada="productos",
                registro_id=codigo_producto
            )
            db.session.add(log)
            db.session.commit()
            return {"status": "eliminado"}, 200
        except:
            db.session.rollback()
            return {"error": "No se puede eliminar un producto con historial de ventas"}, 400
