from app.models import db, Producto, Categoria, Auditoria

class ProductoService:

    # --- GESTIÓN DE CATEGORÍAS ---

    @staticmethod
    def obtener_categorias():
        """Lista todas las categorías para el panel de administración."""
        return Categoria.query.all()

    @staticmethod
    def guardar_categoria(id_usuario, datos):
        """Crea o edita una categoría (ej: Almuerzos, Bebidas)."""
        id_cat = datos.get('id')
        categoria = Categoria.query.get(id_cat) if id_cat else None

        if categoria:
            categoria.nombre = datos['nombre']
            accion = "EDITAR_CATEGORIA"
        else:
            categoria = Categoria(nombre=datos['nombre'])
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
        return {"status": "ok", "id": categoria.id}

    @staticmethod
    def eliminar_categoria(id_usuario, id_cat):
        """Elimina una categoría si no tiene productos vinculados."""
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


    # --- GESTIÓN DE PRODUCTOS ---

    @staticmethod
    def obtener_todo_el_menu():
        """
        Consulta para la PWA (Celulares). 
        Solo devuelve productos activos y agrupados por categoría.
        """
        categorias = Categoria.query.all()
        menu = []

        for cat in categorias:
            items = [
                {
                    "id": p.codigo_producto,
                    "nombre": p.nombre_producto,
                    "precio": p.precio_producto,
                    "formato": p.formato_producto,
                    "descripcion": p.descripcion_producto
                }
                for p in cat.productos if p.activo
            ]

            if items:
                menu.append({
                    "categoria": cat.nombre,
                    "id_categoria": cat.id,
                    "productos": items
                })

        return menu

    @staticmethod
    def obtener_catalogo_maestro():
        """
        Consulta para el Panel Admin.
        Devuelve TODO (activos e inactivos) para gestión y recordatorio visual.
        """
        productos = Producto.query.all()
        return [
            {
                "id": p.codigo_producto,
                "nombre": p.nombre_producto,
                "precio": p.precio_producto,
                "formato": p.formato_producto,
                "descripcion": p.descripcion_producto,
                "categoria": p.categoria.nombre,
                "categoria_id": p.categoria_id,
                "activo": p.activo  # Crucial para el sombreado/gris en UI
            }
            for p in productos
        ]

    @staticmethod
    def crear_o_actualizar_producto(id_usuario, datos):
        """Gestiona el catálogo: permite crear, editar o reactivar productos."""
        codigo = datos.get('codigo_producto')
        producto = Producto.query.get(codigo) if codigo else None

        if producto:
            producto.nombre_producto = datos.get('nombre_producto', producto.nombre_producto)
            producto.precio_producto = datos.get('precio_producto', producto.precio_producto)
            producto.descripcion_producto = datos.get('descripcion_producto', producto.descripcion_producto)
            producto.formato_producto = datos.get('formato_producto', producto.formato_producto)
            producto.categoria_id = datos.get('categoria_id', producto.categoria_id)
            # Permite reactivar un producto inactivo desde la misma edición
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
        return {"status": "ok", "id": producto.codigo_producto}

    @staticmethod
    def set_estado_producto(id_usuario, codigo_producto, estado=False):
        """Activa o desactiva (borrado lógico) un producto."""
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
