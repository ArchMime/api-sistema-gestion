from app.models import db, Venta, ProductoVendido, Producto, Auditoria, Caja
from sqlalchemy.exc import SQLAlchemyError

class VentaService:

    @staticmethod
    def gestionar_venta(id_usuario, id_venta=None, cliente="Consumo Local", productos=[], estado="PENDIENTE"):
        """
        Crea una venta nueva o agrega productos a una cuenta abierta.
        Blindado contra errores de base de datos y validaciones de caja.
        """
        try:
            # 1. VALIDACIÓN DE CAJA: No se puede vender si no hay caja abierta
            caja_activa = Caja.query.filter_by(estado_caja='ABIERTA').first()
            if not caja_activa:
                return {"error": "No se pueden gestionar ventas sin una caja abierta"}, 400

            # 2. OBTENER O CREAR LA CABECERA (VENTA)
            if id_venta:
                venta = Venta.query.get(id_venta)
                if not venta:
                    return {"error": "Venta no encontrada"}, 404
                if venta.estado_pago != 'PENDIENTE':
                    return {"error": f"No se pueden añadir productos a una venta en estado {venta.estado_pago}"}, 400
            else:
                # Nueva venta vinculada a la caja y usuario actual
                venta = Venta(
                    cliente=cliente,
                    estado_pago=estado,
                    id_caja_fk=caja_activa.id_caja,
                    usuario_id=id_usuario
                )
                db.session.add(venta)
                db.session.flush() # Para obtener el id_venta antes de los detalles

            # 3. PROCESAR EL LISTADO DE PRODUCTOS
            for item in productos:
                # Validación mínima de datos del item
                id_prod = item.get('id_producto')
                cantidad = item.get('cantidad', 0)
                
                if not id_prod or cantidad <= 0:
                    continue

                prod_catalogo = Producto.query.get(id_prod)

                if prod_catalogo and prod_catalogo.activo:
                    nuevo_detalle = ProductoVendido(
                        id_venta_fk=venta.id_venta,
                        id_producto_fk=prod_catalogo.codigo_producto,
                        cantidad=cantidad,
                        precio_unitario=prod_catalogo.precio_producto # Congelamos precio histórico
                    )

                    # Actualizamos el total de la cabecera
                    venta.total += (cantidad * prod_catalogo.precio_producto)
                    db.session.add(nuevo_detalle)

                    # Auditoría del movimiento operativo
                    db.session.add(Auditoria(
                        usuario_id=id_usuario,
                        accion="AGREGAR_PRODUCTO",
                        tabla_afectada="productos_vendidos",
                        registro_id=venta.id_venta
                    ))

            db.session.commit()
            return {
                "status": "success", 
                "id_venta": venta.id_venta, 
                "total_acumulado": venta.total
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos al gestionar venta", "detalle": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Error inesperado", "detalle": str(e)}, 500

    @staticmethod
    def finalizar_pago(id_usuario, id_venta, forma_pago, propina=0):
        """
        Cierra una cuenta abierta y registra el ingreso de dinero.
        """
        try:
            # Validamos caja activa
            caja_activa = Caja.query.filter_by(estado_caja='ABIERTA').first()
            if not caja_activa:
                return {"error": "La caja está cerrada. Reábrala para procesar el pago."}, 400

            venta = Venta.query.get(id_venta)
            if not venta:
                return {"error": "Venta no encontrada"}, 404
            
            if venta.estado_pago == 'PAGADO':
                return {"error": "Esta venta ya fue pagada anteriormente"}, 400
            
            if venta.estado_pago == 'ANULADO':
                return {"error": "No se puede cobrar una venta anulada"}, 400

            # Verificación de integridad: la venta debe ser de la caja actual
            if venta.id_caja_fk != caja_activa.id_caja:
                return {"error": "Esta venta pertenece a una sesión de caja distinta"}, 400

            # Registrar el pago
            venta.estado_pago = 'PAGADO'
            venta.forma_pago = forma_pago
            venta.propina = propina
            venta.usuario_id = id_usuario # Registramos quién hizo el cobro final

            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="CERRAR_VENTA_PAGO",
                tabla_afectada="ventas",
                registro_id=id_venta
            ))

            db.session.commit()
            return {"status": "success", "mensaje": "Pago registrado con éxito", "total": venta.total}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos al finalizar pago", "detalle": str(e)}, 500

    @staticmethod
    def anular_venta(id_usuario, id_venta, motivo="Cancelación de pedido"):
        """
        Invalida una venta pendiente (borrado lógico).
        """
        try:
            venta = Venta.query.get(id_venta)
            if not venta:
                return {"error": "Venta no encontrada"}, 404
            
            if venta.estado_pago == 'PAGADO':
                return {"error": "No se puede anular una venta que ya fue pagada"}, 400
            
            venta.estado_pago = 'ANULADO'
            venta.total = 0 # El monto deja de sumar para la caja

            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion=f"ANULAR_VENTA: {motivo}",
                tabla_afectada="ventas",
                registro_id=id_venta
            ))

            db.session.commit()
            return {"status": "success", "mensaje": f"Venta {id_venta} anulada"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error al anular venta", "detalle": str(e)}, 500

    @staticmethod
    def obtener_ventas_pendientes():
        """
        Retorna la lista de cuentas abiertas (útil para la Persona C antes de cerrar caja).
        """
        try:
            pendientes = Venta.query.filter_by(estado_pago='PENDIENTE').all()
            return [
                {
                    "id_venta": v.id_venta,
                    "cliente": v.cliente,
                    "total": v.total,
                    "hora": v.hora_venta
                } for v in pendientes
            ], 200
        except Exception as e:
            return {"error": "No se pudieron recuperar las ventas pendientes", "detalle": str(e)}, 500
