from app.models import db, Venta, ProductoVendido, Producto, Auditoria
from datetime import datetime

class VentaService:

    @staticmethod
    def gestionar_venta(id_usuario, id_venta=None, cliente="Publico General", productos=[], estado="PENDIENTE"):
        """
        Crea una venta nueva o agrega productos a una existente.
        'productos' debe ser una lista de dicts: [{'id_producto': 1, 'cantidad': 2}, ...]
        """
        # 1. Obtener o crear la Venta (Cabecera)
        if id_venta:
            venta = Venta.query.get(id_venta)
            if not venta:
                return {"error": "Venta no encontrada"}, 404
            if venta.estado_pago == 'PAGADO':
                return {"error": "No se pueden agregar productos a una venta cerrada"}, 400
        else:
            venta = Venta(cliente=cliente, estado_pago=estado)
            db.session.add(venta)
            db.session.flush() # Genera el ID para los productos vendidos

        # 2. Loop de productos con validación (Tu lógica de filtro)
        for item in productos:
            prod_catalogo = Producto.query.get(item['id_producto'])
            
            if prod_catalogo:
                # Insertamos un registro nuevo (aunque ya existan otros iguales en la mesa)
                nuevo_detalle = ProductoVendido(
                    id_venta_fk=venta.id_venta,
                    id_producto_fk=prod_catalogo.codigo_producto,
                    cantidad=item['cantidad'],
                    precio_unitario=prod_catalogo.precio_producto
                )
                
                # Actualizar total de la cabecera
                subtotal = item['cantidad'] * prod_catalogo.precio_producto
                venta.total += subtotal
                
                db.session.add(nuevo_detalle)

                # 3. Registro de Auditoría (Trazabilidad)
                log = Auditoria(
                    usuario_id=id_usuario,
                    accion="AGREGAR_PRODUCTO",
                    tabla_afectada="productos_vendidos",
                    registro_id=venta.id_venta # Vinculamos al ID de la venta
                )
                db.session.add(log)

        db.session.commit()
        return {"id_venta": venta.id_venta, "total": venta.total}, 200

    @staticmethod
    def finalizar_pago(id_usuario, id_venta, forma_pago, propina=0):
        """Cierra la venta y registra el movimiento en auditoría."""
        venta = Venta.query.get(id_venta)
        
        if not venta or venta.estado_pago == 'PAGADO':
            return {"error": "Venta no válida para cierre"}, 400

        venta.estado_pago = 'PAGADO'
        venta.forma_pago = forma_pago
        venta.propina = propina
        
        # Auditoría del cierre
        log = Auditoria(
            usuario_id=id_usuario,
            accion="CERRAR_VENTA",
            tabla_afectada="ventas",
            registro_id=id_venta
        )
        db.session.add(log)
        
        db.session.commit()
        return {"status": "Venta cerrada con éxito"}, 200
