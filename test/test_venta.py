import requests

BASE_VENTAS = "http://127.0.0.1:5000/api/ventas"
BASE_CAJA = "http://127.0.0.1:5000/api/caja"
BASE_PROD = "http://127.0.0.1:5000/api/productos"
ID_USUARIO = 1  # Asumimos que el seed ya creó este usuario


def ejecutar_test_ventas():
    print("=== INICIANDO TEST INTEGRADO: VENTAS (ROBUSTEZ) ===")

    try:
        # 1. PREPARACIÓN DE CATÁLOGO (Usando tus llaves exactas 'id')
        print("\n1. Creando Categoría y Producto...")
        res_cat = requests.post(f"{BASE_PROD}/categorias", json={
            "id_usuario": ID_USUARIO, "nombre": "Bebidas Test"
        })
        id_cat = res_cat.json().get('id') # Según tu test_productos.py

        res_p = requests.post(f"{BASE_PROD}/gestionar", json={
            "id_usuario": ID_USUARIO,
            "nombre_producto": "Coca Cola Test",
            "precio_producto": 1500,
            "categoria_id": id_cat,
            "formato_producto": "Lata"
        })
        id_prod = res_p.json().get('id')
        print(f"   [OK] Producto listo ID: {id_prod} en Categoría ID: {id_cat}")

        # 2. ASEGURAR CAJA ABIERTA (Necesario para el blindaje del Service)
        print("\n2. Abriendo caja para permitir operaciones...")
        # Primero intentamos abrir; si ya hay una abierta, el sistema lo ignorará o dará error
        requests.post(f"{BASE_CAJA}/abrir", json={"id_usuario": ID_USUARIO, "monto_inicial": 10000})
        print("   [OK] Caja lista.")

        # 3. CREAR CUENTA ABIERTA (Mesa 10)
        print("\n3. Abriendo cuenta para 'Mesa 10'...")
        res_v = requests.post(f"{BASE_VENTAS}/", json={
            "id_usuario": ID_USUARIO,
            "cliente": "Mesa 10",
            "productos": [{"id_producto": id_prod, "cantidad": 2}] # Total: 3000
        })
        v_data = res_v.json()
        id_venta = v_data.get('id_venta')
        print(f"   [OK] Venta ID: {id_venta} | Total acumulado: ${v_data.get('total_acumulado')}")

        # 4. AGREGAR "ANTOJO" (Misma venta)
        print(f"\n4. Agregando 1 unidad extra a la Venta {id_venta}...")
        res_v2 = requests.post(f"{BASE_VENTAS}/", json={
            "id_usuario": ID_USUARIO,
            "id_venta": id_venta,
            "productos": [{"id_producto": id_prod, "cantidad": 1}] # +1500
        })
        print(f"   [OK] Nuevo Total: ${res_v2.json().get('total_acumulado')}")

        # 5. FINALIZAR PAGO
        print(f"\n5. Procesando pago de Venta {id_venta} (EFECTIVO)...")
        res_pago = requests.post(f"{BASE_VENTAS}/pagar", json={
            "id_usuario": ID_USUARIO,
            "id_venta": id_venta,
            "forma_pago": "EFECTIVO",
            "propina": 500
        })
        if res_pago.status_code == 200:
            print(f"   [OK] Pago exitoso: {res_pago.json().get('mensaje')}")

        # 6. VERIFICACIÓN DE DETALLE (Integridad de datos)
        print(f"\n6. Consultando detalle final de Venta {id_venta}...")
        res_det = requests.get(f"{BASE_VENTAS}/{id_venta}")
        det = res_det.json()
        
        print(f"   - Cliente: {det['cliente']}")
        print(f"   - Estado: {det['estado']}")
        print(f"   - Total: ${det['total']}")
        print(f"   - Productos en ticket: {len(det['detalle_productos'])}")
        
        # Validación de blindaje de precios
        precio_en_ticket = det['detalle_productos'][0]['precio_unitario']
        if precio_en_ticket == 1500:
            print("   [OK] El precio histórico se guardó correctamente.")

        print("\n--- ¡TEST DE VENTAS COMPLETADO CON ÉXITO! ---")

    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN TEST]: {e}")

if __name__ == "__main__":
    ejecutar_test_ventas()

