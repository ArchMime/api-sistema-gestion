import requests
import time

BASE_VENTAS = "http://127.0.0.1:5000/api/ventas"
BASE_CAJA = "http://127.0.0.1:5000/api/caja"
BASE_PROD = "http://127.0.0.1:5000/api/productos"
ID_USUARIO = 1


def probar_ventas():
    print("--- INICIANDO TEST COMPLETO DE VENTAS Y CUADRATURA ---")

    try:
        # 1. Preparación de Catálogo (Necesitamos un producto real)
        print("\n1. Creando Categoría y Producto para la prueba...")
        res_cat = requests.post(f"{BASE_PROD}/categorias", json={
            "id_usuario": ID_USUARIO, "nombre": "Sandwich"
        })
        id_cat = res_cat.json().get('id')

        res_p = requests.post(f"{BASE_PROD}/gestionar", json={
            "id_usuario": ID_USUARIO,
            "nombre_producto": "Ave Mayo",
            "precio_producto": 3500,
            "categoria_id": id_cat,
            "formato_producto": "Normal"
        })
        id_prod = res_p.json().get('id')
        print(f"   [OK] Producto 'Ave Mayo' listo con ID: {id_prod}")

        # 2. Gestión de Caja (Asegurar que esté abierta para permitir ventas)
        print("\n2. Verificando estado de caja...")
        res_est = requests.get(f"{BASE_CAJA}/estado").json()
        
        if res_est['estado'] == 'LIBRE':
            print("   [INFO] Abriendo nueva caja...")
            res_c = requests.post(f"{BASE_CAJA}/abrir", json={"id_usuario": ID_USUARIO, "monto_inicial": 10000})
            id_caja = res_c.json().get('id_caja')
        else:
            id_caja = res_est['id_caja']
            if res_est['estado'] == 'EXISTENTE':
                print(f"   [INFO] Reabriendo caja ID: {id_caja}")
                requests.post(f"{BASE_CAJA}/reabrir", json={"id_usuario": ID_USUARIO, "id_caja": id_caja})
        
        print(f"   [OK] Caja lista para operar (ID: {id_caja})")

        # 3. Flujo de Venta: Crear Pedido
        print(f"\n3. Creando pedido en Mesa 5 (2 unidades de producto {id_prod})...")
        res_v = requests.post(f"{BASE_VENTAS}/", json={
            "id_usuario": ID_USUARIO,
            "cliente": "Mesa 5",
            "productos": [{"id_producto": id_prod, "cantidad": 2}]
        })
        id_v = res_v.json().get('id_venta')
        total_v = res_v.json().get('total')
        print(f"   [OK] Venta registrada ID: {id_v} | Total: ${total_v}")

        # 4. Flujo de Venta: Finalizar Pago
        print(f"\n4. Procesando pago de la venta {id_v} en EFECTIVO...")
        requests.post(f"{BASE_VENTAS}/pagar", json={
            "id_usuario": ID_USUARIO,
            "id_venta": id_v,
            "forma_pago": "EFECTIVO",
            "propina": 0
        })
        print("   [OK] Pago procesado.")

        # 5. Cierre de Caja para Recalcular Totales
        # Cálculo esperado: 10,000 inicial + 7,000 venta = 17,000
        print("\n5. Cerrando caja para ejecutar arqueo y sumatoria de ventas...")
        res_cier = requests.post(f"{BASE_CAJA}/cerrar", json={
            "id_usuario": ID_USUARIO,
            "efectivo_fisico": 17000,
            "observaciones": "Cierre de test de ventas"
        })
        
        if res_cier.status_code == 200:
            # 6. Verificación Final en Historial
            print("\n6. Verificando impacto en el historial administrativo...")
            res_hist = requests.get(f"{BASE_CAJA}/historial").json()
            # Buscamos la caja actual en la lista
            caja_data = next(c for c in res_hist if c['id'] == id_caja)
            
            print(f"   [RESULTADO FINAL]")
            print(f"   - Estado Caja: {caja_data['estado']}")
            print(f"   - Total Ventas: ${caja_data['total_ventas']}")
            print(f"   - Diferencia Arqueo: ${caja_data['diferencia']}")
            
            if caja_data['total_ventas'] == total_v:
                print("\n--- ¡TEST COMPLETADO CON ÉXITO! ---")
            else:
                print("\n--- [ALERTA] Los totales no coinciden con la venta registrada ---")

    except Exception as e:
        print(f"\n   [ERROR CRÍTICO] Ocurrió un fallo durante el test: {e}")

if __name__ == "__main__":
    probar_ventas()

def probar_ventas():
    print("--- INICIANDO TEST DEL MÓDULO VENTAS (AUTÓNOMO) ---")

    # 1. Preparación: Crear Categoría y Producto
    print("\n1. Preparando catálogo (Creando 'Ave Mayo' a $3500)...")
    res_cat = requests.post(f"{BASE_PROD}/categorias", json={"id_usuario": ID_USUARIO, "nombre": "Sandwich"})
    id_cat = res_cat.json().get('id')
    
    res_p = requests.post(f"{BASE_PROD}/gestionar", json={
        "id_usuario": ID_USUARIO, "nombre_producto": "Ave Mayo",
        "precio_producto": 3500, "categoria_id": id_cat, "formato_producto": "Normal"
    })
    id_producto = res_p.json().get('id')
    print(f"   [OK] Producto listo con ID: {id_producto}")

    # 2. Asegurar Caja Abierta
    print("\n2. Reabriendo caja ID 1...")
    requests.post(f"{BASE_CAJA}/reabrir", json={"id_usuario": ID_USUARIO, "id_caja": 1})

    # 3. Crear venta con productos reales
    print(f"\n3. Vendiendo 2 '{id_producto}' a Mesa 5...")
    res_venta = requests.post(f"{BASE_VENTAS}/", json={
        "id_usuario": ID_USUARIO,
        "cliente": "Mesa 5",
        "productos": [{"id_producto": id_producto, "cantidad": 2}]
    })
    id_v = res_venta.json().get('id_venta')
    print(f"   [OK] Venta creada ID: {id_v} | Total: {res_venta.json().get('total')}")

    # 4. Finalizar Pago
    print("\n4. Pagando venta...")
    requests.post(f"{BASE_VENTAS}/pagar", json={
        "id_usuario": ID_USUARIO, "id_venta": id_v, "forma_pago": "EFECTIVO"
    })

    # 5. Volver a cerrar la caja para que recalcule totales
    print("\n5. Cerrando caja para procesar arqueo final...")
    requests.post(f"{BASE_CAJA}/cerrar", json={
        "id_usuario": ID_USUARIO,
        "efectivo_fisico": 12000 # 10k inicial - 5k egreso + 7k venta
    })

    # 6. Verificación final
    print("\n6. Verificando impacto real en el historial...")
    res_hist = requests.get(f"{BASE_CAJA}/historial")
    caja = next(c for c in res_hist.json() if c['id'] == 1)
    print(f"   [RESULTADO] Total Ventas en Caja: ${caja['total_ventas']}")


if __name__ == "__main__":
    probar_ventas()


