import requests

BASE_CAJA = "http://127.0.0.1:5000/api/caja"
BASE_VENTAS = "http://127.0.0.1:5000/api/ventas"
ID_USUARIO = 1 # Admin/Sistema

def ejecutar_test_caja():
    print("=== INICIANDO TEST DE ROBUSTEZ: MÓDULO CAJA ===")

    # 1. TEST: Apertura Duplicada
    print("\n1. Intentando abrir una caja cuando ya hay una abierta...")
    res = requests.post(f"{BASE_CAJA}/abrir", json={
        "id_usuario": ID_USUARIO,
        "monto_inicial": 5000
    })
    if res.status_code == 400:
        print(f"   [OK] Bloqueado correctamente: {res.json().get('error')}")
    else:
        print(f"   [FALLO] El sistema permitió abrir dos cajas simultáneas.")

    # 2. TEST: Egreso Inválido (Monto negativo)
    print("\n2. Intentando registrar egreso negativo...")
    res = requests.post(f"{BASE_CAJA}/egreso", json={
        "id_usuario": ID_USUARIO,
        "monto": -1000,
        "descripcion": "Robo fantasma",
        "categoria": "VARIOS"
    })
    if res.status_code == 400:
        print(f"   [OK] Egreso negativo rechazado.")
    else:
        print(f"   [FALLO] Se aceptó un egreso negativo.")

    # 3. TEST: Registro de Egreso Exitoso
    print("\n3. Registrando egreso válido ($2.000 para pan)...")
    res_eg = requests.post(f"{BASE_CAJA}/egreso", json={
        "id_usuario": ID_USUARIO,
        "monto": 2000,
        "descripcion": "Compra de pan",
        "categoria": "INSUMOS"
    })
    if res_eg.status_code == 201:
        print(f"   [OK] Egreso registrado en la sesión actual.")

    # 4. TEST: Bloqueo de Cierre por Venta Pendiente
    print("\n4. Creando venta PENDIENTE y tratando de cerrar caja...")
    # Abrimos una cuenta nueva (Mesa 5) pero NO la pagamos
    res_v = requests.post(f"{BASE_VENTAS}/", json={
        "id_usuario": ID_USUARIO,
        "cliente": "Mesa 5 - Olvidada",
        "productos": [{"id_producto": 1, "cantidad": 1}]
    })
    
    # Intentamos cerrar la caja
    res_cierre = requests.post(f"{BASE_CAJA}/cerrar", json={
        "id_usuario": ID_USUARIO,
        "efectivo_fisico": 10000
    })
    if res_cierre.status_code == 400:
        print(f"   [OK] CIERRE BLOQUEADO: {res_cierre.json().get('detalle')}")
        print("   [INFO] El blindaje detectó la venta pendiente exitosamente.")
    else:
        print(f"   [FALLO] ¡La caja se cerró con ventas pendientes!")

    # 5. TEST: Cuadratura Final (Flujo Limpio)
    print("\n5. Resolviendo pendiente y ejecutando cierre final...")
    # Primero pagamos la venta pendiente para liberar la caja
    id_v_pendiente = res_v.json().get('id_venta')
    requests.post(f"{BASE_VENTAS}/pagar", json={
        "id_usuario": ID_USUARIO, "id_venta": id_v_pendiente, "forma_pago": "EFECTIVO"
    })

    # Ahora cerramos con cuadratura
    # Supongamos: Inicial(10.000) + Venta1(4.500) + Venta2(1.500 aprox) - Egreso(2.000)
    # Enviamos un monto físico para ver la diferencia
    res_final = requests.post(f"{BASE_CAJA}/cerrar", json={
        "id_usuario": ID_USUARIO,
        "efectivo_fisico": 14000,
        "observaciones": "Test final de jornada"
    })
    
    if res_final.status_code == 200:
        data = res_final.json().get('data')
        print(f"   [ÉXITO] Caja cerrada correctamente.")
        print(f"   - Saldo Esperado: ${data['esperado']}")
        print(f"   - Saldo Físico: ${data['fisico']}")
        print(f"   - Diferencia: ${data['diferencia']}")

if __name__ == "__main__":
    ejecutar_test_caja()
