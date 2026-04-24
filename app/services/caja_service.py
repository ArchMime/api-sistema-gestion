from app.models import db, Caja, Egreso, Venta, Auditoria
from datetime import datetime

class CajaService:

    @staticmethod
    def abrir_caja(id_usuario, monto_inicial):
        """Inicia el día con un monto base en efectivo."""
        fecha_hoy = datetime.now().strftime("%d-%m-%Y")
        
        # Validamos que no exista una caja ya abierta para hoy
        caja_existente = Caja.query.filter_by(fecha=fecha_hoy).first()
        if caja_existente:
            return {"error": "La caja de hoy ya fue abierta"}, 400

        nueva_caja = Caja(
            fecha=fecha_hoy,
            saldo_inicial=monto_inicial,
            estado_caja='ABIERTA'
        )
        db.session.add(nueva_caja)
        
        # Auditoría
        log = Auditoria(
            usuario_id=id_usuario, 
            accion="ABRIR_CAJA", 
            tabla_afectada="caja"
        )
        db.session.add(log)
        
        db.session.commit()
        return {"status": "Caja abierta", "id_caja": nueva_caja.id_caja}, 201

    @staticmethod
    def registrar_egreso(id_usuario, monto, descripcion, categoria):
        """Registra una salida de dinero (insumos, propinas, etc.)."""
        nuevo_egreso = Egreso(
            monto=monto,
            descripcion_egreso=descripcion,
            categoria=categoria,
            usuario_id=id_usuario
        )
        db.session.add(nuevo_egreso)
        
        # Flush para obtener el ID antes del commit para la auditoría
        db.session.flush()
        
        log = Auditoria(
            usuario_id=id_usuario, 
            accion="REGISTRAR_EGRESO", 
            tabla_afectada="egresos", 
            registro_id=nuevo_egreso.id_egreso
        )
        db.session.add(log)
        
        db.session.commit()
        return {"status": "Egreso registrado"}, 201

    @staticmethod
    def cerrar_caja(id_usuario, efectivo_fisico, observaciones=""):
        """Calcula totales del día y cierra la caja."""
        fecha_hoy = datetime.now().strftime("%d-%m-%Y")
        caja = Caja.query.filter_by(fecha=fecha_hoy, estado_caja='ABIERTA').first()

        if not caja:
            return {"error": "No hay una caja abierta para cerrar"}, 400

        # 1. Sumamos Ventas del día por método de pago
        ventas_hoy = Venta.query.filter_by(fecha_venta=fecha_hoy, estado_pago='PAGADO').all()
        
        efectivo_ventas = sum(v.total for v in ventas_hoy if v.forma_pago == 'EFECTIVO')
        tarjeta = sum(v.total for v in ventas_hoy if v.forma_pago == 'TARJETA')
        transferencia = sum(v.total for v in ventas_hoy if v.forma_pago == 'TRANSFERENCIA')

        # 2. Sumamos Egresos del día
        egresos_hoy = Egreso.query.filter_by(fecha_egreso=fecha_hoy).all()
        total_egresos = sum(e.monto for e in egresos_hoy)

        # 3. Cálculo de cuadratura
        # Saldo esperado = Lo que había al iniciar + ventas en efectivo - gastos en efectivo
        saldo_esperado = caja.saldo_inicial + efectivo_ventas - total_egresos
        diferencia = efectivo_fisico - saldo_esperado

        # 4. Actualizamos el registro de Caja
        caja.movimientos_efectivo = efectivo_ventas
        caja.movimientos_tarjeta = tarjeta
        caja.movimientos_transferencia = transferencia
        caja.saldo_final_efectivo = efectivo_fisico
        caja.diferencia_efectivo = diferencia
        caja.observaciones = observaciones
        caja.estado_caja = 'CERRADA'
        caja.usuario_id = id_usuario

        # Auditoría del cierre
        log = Auditoria(
            usuario_id=id_usuario, 
            accion="CERRAR_CAJA", 
            tabla_afectada="caja", 
            registro_id=caja.id_caja
        )
        db.session.add(log)

        db.session.commit()
        
        return {
            "status": "Caja cerrada",
            "saldo_esperado": saldo_esperado,
            "diferencia": diferencia
        }, 200

    @staticmethod
    def corregir_cierre_caja(id_usuario, id_caja, nuevo_efectivo_fisico, motivo):
        """Permite corregir el monto contado en caso de error humano."""
        caja = Caja.query.get(id_caja)
        
        if not caja:
            return {"error": "Registro de caja no encontrado"}, 404
        
        # Recuperamos el saldo esperado original a partir de los datos guardados
        # Saldo esperado = Final - Diferencia (deshacemos el cálculo anterior)
        saldo_esperado = caja.saldo_final_efectivo - caja.diferencia_efectivo
        
        valor_anterior = caja.saldo_final_efectivo
        caja.saldo_final_efectivo = nuevo_efectivo_fisico
        caja.diferencia_efectivo = nuevo_efectivo_fisico - saldo_esperado
        caja.observaciones = f"{caja.observaciones} | CORRECCIÓN: {motivo}"

        # Auditoría obligatoria para trazabilidad
        log = Auditoria(
            usuario_id=id_usuario, 
            accion="CORREGIR_CIERRE_CAJA", 
            tabla_afectada="caja", 
            registro_id=id_caja
        )
        db.session.add(log)
        
        db.session.commit()
        
        return {
            "status": "Caja corregida",
            "antes": valor_anterior,
            "ahora": nuevo_efectivo_fisico,
            "nueva_diferencia": caja.diferencia_efectivo
        }, 200
