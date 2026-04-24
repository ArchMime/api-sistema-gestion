import requests
import json

# Ajustado con el prefijo /api/auth que definiste en el __init__.py
BASE_URL = "http://127.0.0.1:5000/api/auth"

def probar_flujo_seguridad():
    print("--- INICIANDO TEST DE FLUJO DE USUARIOS (API) ---")

    # 1. EL CELULAR SOLICITA ACCESO
    print("\n1. Simulando celular solicitando acceso...")
    payload_solicitud = {"nombre_dispositivo": "Samsung de Persona C"}
    try:
        res_solicitud = requests.post(f"{BASE_URL}/solicitar-acceso", json=payload_solicitud)
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al servidor. ¿Está 'python run.py' activo?")
        return

    if res_solicitud.status_code == 202:
        token = res_solicitud.json().get("token")
        print(f"   [OK] Token recibido: {token[:8]}...")
    else:
        print(f"   [ERROR] Código {res_solicitud.status_code}: {res_solicitud.text}")
        return

    # 2. VALIDAR QUE ESTÁ PENDIENTE
    print("\n2. Verificando que el token esté en estado PENDIENTE...")
    res_val_1 = requests.post(f"{BASE_URL}/validar-token", json={"token": token})
    # Esperamos un 401 porque aún no tiene usuario asignado
    if res_val_1.status_code == 401:
        print(f"   [OK] Respuesta correcta: {res_val_1.json().get('status')}")
    else:
        print(f"   [AVISO] Status inesperado: {res_val_1.status_code}")

    # 3. EL PANEL DE CONTROL (ADMIN) APRUEBA EL ACCESO
    # Persona C suele ser ID 4 (Sistema=1, A=2, B=3, C=4)
    print("\n3. Simulando aprobación desde el Panel de Control (Admin)...")
    payload_aprobacion = {
        "token": token,
        "usuario_id": 3, 
        "admin_id": 0    
    }
    res_aprob = requests.post(f"{BASE_URL}/admin/aprobar-acceso", json=payload_aprobacion)
    
    if res_aprob.status_code == 200:
        print("   [OK] Dispositivo autorizado exitosamente.")
    else:
        print(f"   [ERROR] Falló la aprobación (Revisa si el ID 4 existe): {res_aprob.text}")
        return

    # 4. EL CELULAR REINTENTA ENTRAR
    print("\n4. Celular reintentando validar su token ya aprobado...")
    res_val_2 = requests.post(f"{BASE_URL}/validar-token", json={"token": token})
    
    if res_val_2.status_code == 200:
        datos = res_val_2.json()
        print(f"   [ÉXITO TOTAL] Bienvenida, {datos['usuario']['nombre']}!")
        print(f"   Rol: {datos['usuario']['rol']}")
    else:
        print(f"   [ERROR] El token sigue sin ser válido. Status: {res_val_2.status_code}")

if __name__ == "__main__":
    probar_flujo_seguridad()

