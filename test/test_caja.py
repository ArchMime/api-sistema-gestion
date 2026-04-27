import requests

BASE_URL = "http://127.0.0.1:5000/api/caja"
ID_USUARIO = 1  # Administrador

def probar_caja():
    print("--- INICIANDO TEST DEL MÓDULO CAJA ---")

    # 1. Verificar estado inicial (Debería estar LIBRE o EXISTENTE)
    print("\n1. Consultando estado inicial de la caja...")
    res_estado = requests.get(f"{BASE_URL}/estado")
    estado_data = res_estado.json()
    print(f"   [INFO] Estado actual: {estado_data['estado']} - {estado_data['mensaje']}")

    if estado_data['estado'] == 'BLOQUEADO':
        print("   [!] La caja ya está abierta. CIÉRRELA manualmente antes de correr el test.")
        return

    # 2. Abrir Caja
    print("\n2. Abriendo caja con $10.000...")
    res_abrir = requests.post(f"{BASE_URL}/abrir", json={
        "id_usuario": ID_USUARIO,
        "monto_inicial": 10000
    })
    
    if res_abrir.status_code in [200, 201]:
        id_caja = res_abrir.json().get('id_caja')
        print(f"   [OK] Caja abierta ID: {id_caja}")
    else:
        print(f"   [ERROR] {res_abrir.text}")
        return

    # 3. Registrar un Egreso (Gasto)
    print("\n3. Registrando gasto de 'Gas' por $5.000...")
    res_egreso = requests.post(f"{BASE_URL}/egreso", json={
        "id_usuario": ID_USUARIO,
        "monto": 5000,
        "descripcion": "Cilindro de gas 15kg",
        "categoria": "INSUMOS"
    })
    
    if res_egreso.status_code == 201:
        print("   [OK] Egreso registrado correctamente.")
    else:
        print(f"   [ERROR] {res_egreso.text}")

    # 4. Cerrar Caja con Arqueo
    # Lógica: Iniciamos con 10k, gastamos 5k -> Debería haber 5k.
    # Vamos a decir que contamos 4k para forzar una diferencia de -1k.
    print("\n4. Cerrando caja (Arqueo físico: $4.000)...")
    res_cerrar = requests.post(f"{BASE_URL}/cerrar", json={
        "id_usuario": ID_USUARIO,
        "efectivo_fisico": 4000,
        "observaciones": "Test de descuadre intencional"
    })

    if res_cerrar.status_code == 200:
        data = res_cerrar.json()
        print(f"   [OK] Caja cerrada.")
        print(f"   [DATA] Esperado: {data['esperado']} | Diferencia: {data['diferencia']}")
    else:
        print(f"   [ERROR] {res_cerrar.text}")

    # 5. Verificar Historial (Panel Admin)
    print("\n5. Verificando persistencia en Historial Administrativo...")
    res_historial = requests.get(f"{BASE_URL}/historial")
    if res_historial.status_code == 200:
        ultima_caja = res_historial.json()[0] # La primera es la más reciente
        print(f"   [OK] Última caja en historial ID: {ultima_caja['id']} | Estado: {ultima_caja['estado']}")
    else:
        print("   [ERROR] No se pudo obtener el historial.")

if __name__ == "__main__":
    probar_caja()
