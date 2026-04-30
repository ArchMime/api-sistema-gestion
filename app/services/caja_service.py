from app.models import db, Caja, Egreso, Venta, Auditoria
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class CajaService:

    @staticmethod
    def verificar_estado_diario():
        try:
            fecha_hoy = datetime.now().strftime("%d-%m-%Y")
            caja_abierta = Caja.query.filter_by(estado_caja='ABIERTA').first()
            
            if caja_abierta:
                return {"estado": "BLOQUEADO", "mensaje": "Hay una caja abierta", "id_caja": caja_abierta.id_caja}, 200

            caja_hoy = Caja.query.filter_by(fecha=fecha_hoy).first()
            if caja_hoy:
                return {
                    "estado": "EXISTENTE",
                    "mensaje": "Ya existe una caja de hoy",
                    "id_caja": caja_hoy.id_caja,
                    "ultima_hora": caja_hoy.hora_cierre
                }, 200

            return {"estado": "LIBRE", "mensaje": "No hay registros hoy"}, 200
        except Exception as e:
            return {"error": "Error al consultar estado", "detalle": str(e)}, 500

    @staticmethod
    def abrir_caja(id_usuario, monto_inicial, forzar_nueva=False):
        if monto_inicial < 0:
            return {"error": "El monto inicial no puede ser negativo"}, 400
        
        try:
            fecha_hoy = datetime.now().strftime("%d-%m-%Y")
            abierta = Caja.query.filter_by(estado_caja='ABIERTA').first()
            
            if abierta:
                return {"error": f"Debe cerrar la sesión {abierta.id_caja} primero"}, 400

            if not forzar_nueva:
                caja_hoy = Caja.query.filter_by(fecha=fecha_hoy).first()
                if caja_hoy:
                    return {"advertencia": "Ya hay un registro de hoy", "id_caja": caja_hoy.id_caja, "sugerencia": "reabrir"}, 200

            nueva_caja = Caja(
                fecha=fecha_hoy,
                saldo_inicial=monto_inicial,
                estado_caja='ABIERTA',
                usuario_id=id_usuario
            )
            db.session.add(nueva_caja)
            db.session.flush()

            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="ABRIR_CAJA",
                tabla_afectada="caja",
                registro_id=nueva_caja.id_caja
            ))
            db.session.commit()
            return {"status": "ok", "id_caja": nueva_caja.id_caja}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos", "detalle": str(e)}, 500

    @staticmethod
    def registrar_egreso(id_usuario, monto, descripcion, categoria):
        if monto <= 0:
            return {"error": "El monto del egreso debe ser mayor a 0"}, 400
            
        try:
            caja = Caja.query.filter_by(estado_caja='ABIERTA').first()
            if not caja:
                return {"error": "No hay una caja abierta para este egreso"}, 400

            nuevo_egreso = Egreso(
                monto=monto,
                descripcion_egreso=descripcion,
                categoria=categoria,
                usuario_id=id_usuario,
                id_caja_fk=caja.id_caja
            )
            db.session.add(nuevo_egreso)
            db.session.flush()

            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="REGISTRAR_EGRESO",
                tabla_afectada="egresos",
                registro_id=nuevo_egreso.id_egreso
            ))
            db.session.commit()
            return {"status": "ok", "id_egreso": nuevo_egreso.id_egreso}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error al registrar egreso", "detalle": str(e)}, 500

    @staticmethod
    def cerrar_caja(id_usuario, efectivo_fisico, observaciones=""):
        try:
            caja = Caja.query.filter_by(estado_caja='ABIERTA').first()
            if not caja:
                return {"error": "No hay ninguna caja abierta"}, 404

            # --- VALIDACIÓN: VENTAS ABIERTAS ---
            ventas_pendientes = [v for v in caja.ventas if v.estado_pago == 'PENDIENTE']
            if ventas_pendientes:
                return {
                    "error": "No se puede cerrar la caja",
                    "detalle": f"Existen {len(ventas_pendientes)} ventas PENDIENTES. Págalas o anúlalas."
                }, 400

            # Cálculos de cuadratura
            efectivo_ventas = sum(v.total for v in caja.ventas if v.forma_pago == 'EFECTIVO' and v.estado_pago == 'PAGADO')
            tarjeta = sum(v.total for v in caja.ventas if v.forma_pago == 'TARJETA' and v.estado_pago == 'PAGADO')
            transferencia = sum(v.total for v in caja.ventas if v.forma_pago == 'TRANSFERENCIA' and v.estado_pago == 'PAGADO')

            total_egresos = sum(e.monto for e in caja.egresos)

            saldo_esperado = caja.saldo_inicial + efectivo_ventas - total_egresos
            
            caja.movimientos_efectivo = efectivo_ventas
            caja.movimientos_tarjeta = tarjeta
            caja.movimientos_transferencia = transferencia
            caja.saldo_final_efectivo = efectivo_fisico
            caja.diferencia_efectivo = efectivo_fisico - saldo_esperado
            caja.observaciones = observaciones
            caja.estado_caja = 'CERRADA'
            caja.hora_cierre = datetime.now().strftime("%H:%M")

            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="CERRAR_CAJA",
                tabla_afectada="caja",
                registro_id=caja.id_caja
            ))
            db.session.commit()
            return {
                "status": "ok", 
                "data": {
                    "esperado": saldo_esperado, 
                    "fisico": efectivo_fisico,
                    "diferencia": caja.diferencia_efectivo
                }
            }, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error al procesar el cierre", "detalle": str(e)}, 500

    @staticmethod
    def listar_cajas_admin():
        try:
            cajas = Caja.query.order_by(Caja.id_caja.desc()).all()
            resultado = [{
                "id": c.id_caja,
                "fecha": c.fecha,
                "estado": c.estado_caja,
                "apertura": c.saldo_inicial,
                "total_ventas": c.movimientos_efectivo + c.movimientos_tarjeta + c.movimientos_transferencia,
                "gastos": sum(e.monto for e in c.egresos),
                "diferencia": c.diferencia_efectivo,
                "observaciones": c.observaciones
            } for c in cajas]
            return resultado, 200
        except Exception as e:
            return {"error": "No se pudo obtener el historial", "detalle": str(e)}, 500


    @staticmethod
    def reabrir_caja(id_usuario, id_caja):
        """
        Permite volver a poner una caja CERRADA en estado ABIERTA.
        Solo si no hay otra caja abierta actualmente.
        """
        try:
            # 1. Verificar si ya hay alguna caja abierta (no pueden haber dos)
            abierta = Caja.query.filter_by(estado_caja='ABIERTA').first()
            if abierta:
                return {"error": f"Ya existe una sesión abierta (ID: {abierta.id_caja}). Ciérrela primero."}, 400

            # 2. Buscar la caja específica
            caja = Caja.query.get(id_caja)
            if not caja:
                return {"error": "La caja especificada no existe"}, 404
            
            if caja.estado_caja == 'ABIERTA':
                return {"mensaje": "La caja ya está abierta", "id_caja": caja.id_caja}, 200

            # 3. Cambiar estado
            caja.estado_caja = 'ABIERTA'
            caja.hora_cierre = None # Limpiamos la hora de cierre anterior
            
            # 4. Auditar la acción
            db.session.add(Auditoria(
                usuario_id=id_usuario,
                accion="REABRIR_CAJA",
                tabla_afectada="caja",
                registro_id=caja.id_caja
            ))
            
            db.session.commit()
            return {"status": "ok", "mensaje": f"Caja {id_caja} reabierta exitosamente"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Error de base de datos al reabrir", "detalle": str(e)}, 500
