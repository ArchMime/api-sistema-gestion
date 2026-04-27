from app.models import db, Caja, Egreso, Venta, Auditoria
from datetime import datetime

class CajaService:

    @staticmethod
    def verificar_estado_diario():
        """Consulta el estado de la caja para el frontend (PWA)."""
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

    @staticmethod
    def abrir_caja(id_usuario, monto_inicial, forzar_nueva=False):
        """Apertura inteligente: previene duplicados y sugiere reapertura."""
        fecha_hoy = datetime.now().strftime("%d-%m-%Y")
        
        abierta = Caja.query.filter_by(estado_caja='ABIERTA').first()
        if abierta:
            return {"error": f"Cierre la caja {abierta.id_caja} antes de continuar"}, 400

        caja_hoy = Caja.query.filter_by(fecha=fecha_hoy).first()
        if caja_hoy and not forzar_nueva:
            return {
                "advertencia": "Ya existe un registro de hoy",
                "id_caja": caja_hoy.id_caja,
                "sugerencia": "reabrir"
            }, 200

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
            accion="ABRIR_NUEVA_SESION",
            tabla_afectada="caja",
            registro_id=nueva_caja.id_caja
        ))
        db.session.commit()
        return {"status": "Nueva caja abierta", "id_caja": nueva_caja.id_caja}, 201

    @staticmethod
    def reabrir_caja(id_usuario, id_caja):
        """Pone en estado ABIERTA una caja previamente cerrada."""
        caja = Caja.query.get(id_caja)
        if not caja: return {"error": "No existe"}, 404
        
        caja.estado_caja = 'ABIERTA'
        db.session.add(Auditoria(
            usuario_id=id_usuario,
            accion="REAPERTURA_CAJA",
            tabla_afectada="caja",
            registro_id=id_caja
        ))
        db.session.commit()
        return {"status": "Caja reabierta con éxito"}, 200

    @staticmethod
    def registrar_egreso(id_usuario, monto, descripcion, categoria):
        """Registra un egreso vinculado a la caja activa."""
        caja = Caja.query.filter_by(estado_caja='ABIERTA').first()
        if not caja:
            return {"error": "No se pueden registrar egresos sin una caja abierta"}, 400

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
        return {"status": "Egreso registrado"}, 201

    @staticmethod
    def cerrar_caja(id_usuario, efectivo_fisico, observaciones=""):
        """Calcula cuadratura y cierra la sesión."""
        caja = Caja.query.filter_by(estado_caja='ABIERTA').first()
        if not caja:
            return {"error": "No hay una caja abierta para cerrar"}, 400

        # Cálculos usando las relaciones del modelo
        efectivo_ventas = sum(v.total for v in caja.ventas if v.forma_pago == 'EFECTIVO' and v.estado_pago == 'PAGADO')
        tarjeta = sum(v.total for v in caja.ventas if v.forma_pago == 'TARJETA' and v.estado_pago == 'PAGADO')
        transferencia = sum(v.total for v in caja.ventas if v.forma_pago == 'TRANSFERENCIA' and v.estado_pago == 'PAGADO')
        
        total_egresos = sum(e.monto for e in caja.egresos)

        saldo_esperado = caja.saldo_inicial + efectivo_ventas - total_egresos
        
        # Actualización de datos de cierre
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
            "status": "Caja cerrada", 
            "esperado": saldo_esperado, 
            "diferencia": caja.diferencia_efectivo
        }, 200

    @staticmethod
    def listar_cajas_admin():
        """Historial para el panel de administración."""
        cajas = Caja.query.order_by(Caja.id_caja.desc()).all()
        return [{
            "id": c.id_caja,
            "fecha": c.fecha,
            "estado": c.estado_caja,
            "apertura": c.saldo_inicial,
            "total_ventas": c.movimientos_efectivo + c.movimientos_tarjeta + c.movimientos_transferencia,
            "gastos": sum(e.monto for e in c.egresos),
            "diferencia": c.diferencia_efectivo,
            "observaciones": c.observaciones
        } for c in cajas], 200
