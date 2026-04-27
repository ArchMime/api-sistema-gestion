from app.models import db, Venta, ProductoVendido, Producto, Auditoria, Caja
from datetime import datetime

class VentaService:

    @staticmethod
    def gestionar_venta(id_usuario, id_venta=None, cliente="Publico General", productos=[], estado="PENDIENTE"):
        # 1. VALIDACIÓN DE CAJA: No se puede vender si no hay caja abierta
        caja_activa = Caja.query.filter_by(estado_caja='ABIERTA').first()
        if not caja_activa:
            return {"error": "No se pueden gestionar ventas sin una caja abierta"}, 400

        # 2. Obtener o crear la Venta (Cabecera)
        if id_venta:
            venta = Venta.query.get(id_venta)
            if not venta:
                return {"error": "Venta no encontrada"}, 404
            if venta.estado_pago == 'PAGADO':
                return {"error": "No se pueden agregar productos a una venta ya pagada"}, 400
        else:
            # Vinculamos la venta a la caja activa y al usuario
            venta = Venta(
                cliente=cliente, 
                estado_pago=estado, 
                id_caja_fk=caja_activa.id_caja,
                usuario_id=id_usuario
            )
            db.session.add(venta)
            db.session.flush()

        # 3. Procesar productos
        for item in productos:
            prod_catalogo = Producto.query.get(item['id_producto'])

            if prod_catalogo and prod_catalogo.activo: # Verificamos que esté activo (borrado lógico)
                nuevo_detalle = ProductoVendido(
                    id_venta_fk=venta.id_venta,
                    id_producto_fk=prod_catalogo.codigo_producto,
                    cantidad=item['cantidad'],
                    precio_unitario=prod_catalogo.precio_producto
                )

                venta.total += (item['cantidad'] * prod_catalogo.precio_producto)
                db.session.add(nuevo_detalle)

                db.session.add(Auditoria(
                    usuario_id=id_usuario,
                    accion="AGREGAR_PRODUCTO",
                    tabla_afectada="productos_vendidos",
                    registro_id=venta.id_venta
                ))

        db.session.commit()
        return {"id_venta": venta.id_venta, "total": venta.total}, 200

    @staticmethod
    def finalizar_pago(id_usuario, id_venta, forma_pago, propina=0):
        # Validamos que la caja siga abierta al momento de pagar
        caja_activa = Caja.query.filter_by(estado_caja='ABIERTA').first()
        if not caja_activa:
            return {"error": "Caja cerrada. Reabra la caja para procesar el pago"}, 400

        venta = Venta.query.get(id_venta)

        if not venta or venta.estado_pago == 'PAGADO':
            return {"error": "Venta no válida o ya pagada"}, 400

        # Aseguramos que la venta pertenezca a la caja que está abierta 
        # (evita pagar ventas de ayer en la caja de hoy si hubo error)
        if venta.id_caja_fk != caja_activa.id_caja:
            return {"error": "Esta venta pertenece a una sesión de caja anterior"}, 400

        venta.estado_pago = 'PAGADO'
        venta.forma_pago = forma_pago
        venta.propina = propina
        venta.usuario_id = id_usuario # El usuario que cobra puede ser distinto al que inició la venta

        db.session.add(Auditoria(
            usuario_id=id_usuario,
            accion="CERRAR_VENTA",
            tabla_afectada="ventas",
            registro_id=id_venta
        ))

        db.session.commit()
        return {"status": "Venta pagada con éxito", "total": venta.total}, 200
