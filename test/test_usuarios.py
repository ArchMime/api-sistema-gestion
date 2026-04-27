import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/auth"

def test_errores_blindaje():
    print("\n--- INICIANDO TEST DE ROBUSTEZ (CASOS DE ERROR) ---")

    # 1. TEST: Duplicar Usuario (Prueba el IntegrityError y Rollback)
    print("\n[ERROR TEST 1] Intentando crear un usuario que ya existe...")
    payload = {"nombre": "Persona A", "rol": "CAJA"}
    # Primer intento (puede que ya exista)
    requests.post(f"{BASE_URL}/admin/usuarios", json=payload)
    # Segundo intento forzado
    res = requests.post(f"{BASE_URL}/admin/usuarios", json=payload)
    
    if res.status_code == 400:
        print(f"   [OK] El servidor rechazó el duplicado correctamente: {res.json().get('error')}")
    else:
        print(f"   [FALLO] El servidor no detectó el duplicado o dio error 500. Status: {res.status_code}")

    # 2. TEST: Datos incompletos (Prueba la validación del controlador)
    print("\n[ERROR TEST 2] Enviando JSON incompleto al crear usuario...")
    res = requests.post(f"{BASE_URL}/admin/usuarios", json={"nombre": "Incompleto"})
    if res.status_code == 400:
        print(f"   [OK] Rechazado por falta de campos.")
    else:
        print(f"   [FALLO] No se validaron campos obligatorios.")

    # 3. TEST: Aprobar Token inexistente
    print("\n[ERROR TEST 3] Intentando aprobar un token que no existe en la DB...")
    payload_fake = {"token": "token-falso-123", "usuario_id": 1}
    res = requests.post(f"{BASE_URL}/admin/aprobar-acceso", json=payload_fake)
    if res.status_code == 404:
        print(f"   [OK] El sistema respondió 'no encontrado' correctamente.")
    else:
        print(f"   [FALLO] Se esperaba 404 para token inexistente.")

    # 4. TEST: Bloqueo de Usuario (Prueba lógica de activo=False)
    print("\n[ERROR TEST 4] Validando token de un usuario BLOQUEADO...")
    # Primero creamos un usuario para la prueba
    user_data = {"nombre": "Usuario Temporal", "rol": "COCINA"}
    u_res = requests.post(f"{BASE_URL}/admin/usuarios", json=user_data).json()
    u_id = u_res.get("id")

    # Solicitamos y aprobamos token
    token = requests.post(f"{BASE_URL}/solicitar-acceso", json={"nombre_dispositivo": "Test"}).json().get("token")
    requests.post(f"{BASE_URL}/admin/aprobar-acceso", json={"token": token, "usuario_id": u_id})

    # Ahora lo bloqueamos
    requests.patch(f"{BASE_URL}/admin/usuarios/{u_id}/estado", json={"activo": False})
    
    # Intentamos validar
    res_val = requests.post(f"{BASE_URL}/validar-token", json={"token": token})
    if res_val.status_code == 401:
        print(f"   [OK] El usuario bloqueado no pudo entrar (401).")
    else:
        print(f"   [FALLO] ¡Un usuario bloqueado pudo validar su token!")

def probar_flujo_exitoso():
    # ... (Tu código original de flujo exitoso aquí) ...
    print("\n--- FLUJO EXITOSO COMPLETADO ---")

if __name__ == "__main__":
    # Primero probamos que lo bueno funciona
    # probar_flujo_exitoso() 
    
    # Luego estresamos el sistema
    test_errores_blindaje()
