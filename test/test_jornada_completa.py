import requests
import time


# 1. Asegúrate de incluir el /api y verificar las barras finales
BASE_CAJA = "http://127.0.0.1:5000/api/caja"
BASE_PROD = "http://127.0.0.1:5000/api/productos"
BASE_VENTA = "http://127.0.0.1:5000/api/ventas"
UID = 1 

def simulacro_jornada():
    print("🚀 INICIANDO SIMULACRO DE JORNADA COMPLETA\n")

    # 1. APERTURA (Ruta: /api/caja/abrir)
    print("1. Apertura de caja con $5.000...")
    res_abrir = requests.post(f"{BASE_CAJA}/abrir", json={"id_usuario": UID, "monto_inicial": 5000})
    
    # 2. CREACIÓN DE PRODUCTO (Ruta: /api/productos/gestionar)
    print("2. Creando 'Empanada' a $2.000...")
    res_p = requests.post(f"{BASE_PROD}/gestionar", json={
        "id_usuario": UID, "nombre_producto": "Empanada Test", "precio_producto": 2000, "categoria_id": 1
    })
    
    if res_p.status_code != 200:
        print(f"   [FALLO] Revisa las rutas en app/__init__.py: {res_p.status_code}")
        return

    id_prod = res_p.json()['id']

    # 3. VENTA (Ruta: /api/ventas/)
    print("3. Operando Mesa 1...")
    res_v = requests.post(f"{BASE_VENTA}/", json={
        "id_usuario": UID, "cliente": "Mesa 1", "productos": [{"id_producto": id_prod, "cantidad": 3}]
    })
    id_v = res_v.json()['id_venta']

    # 4. GASTO (Ruta: /api/caja/egreso)
    print("4. Registrando gasto de $1.500...")
    requests.post(f"{BASE_CAJA}/egreso", json={"id_usuario": UID, "monto": 1500, "descripcion": "Limpieza"})

    # 5. PAGO (Ruta: /api/ventas/pagar)
    print("5. Cobrando Mesa 1 ($6.000)...")
    requests.post(f"{BASE_VENTA}/pagar", json={"id_usuario": UID, "id_venta": id_v, "forma_pago": "EFECTIVO"})

    # 6. CIERRE
    print("\n6. Ejecutando cierre de caja...")
    res_c = requests.post(f"{BASE_CAJA}/cerrar", json={"id_usuario": UID, "efectivo_fisico": 9500})
    
    if res_c.status_code == 200:
        print(f"   [ÉXITO] Cuadratura completada: ${res_c.json()['data']['diferencia']} de diferencia.")
    else:
        print(f"   [ERROR] {res_c.status_code} - {res_c.text}")

if __name__ == "__main__":
    simulacro_jornada()
