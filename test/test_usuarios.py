import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/auth"

def test_flujo_completo_seguridad():
    print("\n--- TEST: FLUJO DE SEGURIDAD (CELULAR -> ADMIN -> VALIDACIÓN) ---")

    # 1. El celular de "Persona B" pide entrar
    print("1. Solicitando acceso desde celular...")
    res_solicitud = requests.post(f"{BASE_URL}/solicitar-acceso", 
                                 json={"nombre_dispositivo": "Samsung Persona B"})
    token = res_solicitud.json().get('token')
    print(f"   [OK] Token recibido: {token[:8]}...")

    # 2. El administrador aprueba el acceso (ID 3 es Persona B según tu seed)
    print("2. Administrador aprueba el acceso para Persona B (ID 3)...")
    requests.post(f"{BASE_URL}/admin/aprobar-acceso", 
                  json={"token": token, "usuario_id": 3, "admin_id": 1})

    # 3. El celular intenta validar su entrada
    print("3. Validando acceso desde el celular...")
    res_val = requests.post(f"{BASE_URL}/validar-token", json={"token": token})
    if res_val.status_code == 200:
        print(f"   [OK] Acceso concedido a: {res_val.json()['usuario']['nombre']}")
    
    # 4. Bloqueamos al usuario y re-intentamos (El punto que te fallaba)
    print("4. Bloqueando a Persona B...")
    requests.patch(f"{BASE_URL}/admin/usuarios/3/estado", 
                   json={"activo": False, "admin_id": 1})
    
    res_val_block = requests.post(f"{BASE_URL}/validar-token", json={"token": token})
    if res_val_block.status_code == 401:
        print("   [OK] Acceso denegado correctamente para usuario bloqueado.")
    else:
        print("   [FALLO] El sistema dejó entrar a un usuario bloqueado.")

if __name__ == "__main__":
    test_flujo_completo_seguridad()
