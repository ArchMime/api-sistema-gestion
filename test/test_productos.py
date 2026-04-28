import requests

BASE_URL = "http://127.0.0.1:5000/api/productos"
# Usamos el ID 3 que genera tu seed.py (Persona B - Cocina)
ID_USUARIO = 3 

def test_productos_blindaje():
    print("\n--- INICIANDO TEST DE ROBUSTEZ: MÓDULO PRODUCTOS ---")

    # 1. TEST: Crear categoría con nombre duplicado
    # La semilla ya crea "Almuerzos", intentaremos crearla de nuevo
    print("\n[ERROR TEST 1] Intentando duplicar categoría 'Almuerzos'...")
    res = requests.post(f"{BASE_URL}/categorias", json={
        "id_usuario": ID_USUARIO,
        "nombre": "Almuerzos"
    })
    if res.status_code in [400, 500]: # SQLAlchemy lanzará IntegrityError
        print(f"   [OK] El servidor controló el duplicado: {res.json().get('error')}")
    else:
        print(f"   [FALLO] Se permitió duplicar una categoría única.")

    # 2. TEST: Crear producto con datos incompletos
    print("\n[ERROR TEST 2] Creando producto sin precio...")
    res = requests.post(f"{BASE_URL}/gestionar", json={
        "id_usuario": ID_USUARIO,
        "nombre_producto": "Producto Fallido",
        "categoria_id": 1
    })
    if res.status_code == 400:
        print(f"   [OK] Rechazado correctamente por falta de datos.")
    else:
        print(f"   [FALLO] El sistema aceptó un producto sin precio.")

    # 3. TEST: Borrar categoría con productos (Integridad Referencial)
    # Primero creamos un producto en la categoría 1
    print("\n[ERROR TEST 3] Intentando borrar categoría con productos vinculados...")
    requests.post(f"{BASE_URL}/gestionar", json={
        "id_usuario": ID_USUARIO,
        "nombre_producto": "Test Borrado",
        "precio_producto": 1000,
        "categoria_id": 1
    })
    # Intentamos borrar la categoría 1 (Almuerzos)
    res = requests.delete(f"{BASE_URL}/categorias/1?id_usuario={ID_USUARIO}")
    if res.status_code == 400:
        print(f"   [OK] Bloqueado: {res.json().get('error')}")
    else:
        print(f"   [FALLO] ¡Se borró una categoría que tenía productos!")

    # 4. TEST: Actualizar producto inexistente
    print("\n[ERROR TEST 4] Intentando editar producto con ID inexistente (999)...")
    res = requests.post(f"{BASE_URL}/gestionar", json={
        "id_usuario": ID_USUARIO,
        "codigo_producto": 999,
        "nombre_producto": "Fantasma",
        "precio_producto": 5000,
        "categoria_id": 1
    })
    # Aquí nuestro Service creará un nuevo producto porque .get(999) devuelve None
    # pero es bueno verificar que no explote.
    if res.status_code == 200:
        print(f"   [INFO] El sistema creó uno nuevo en lugar de fallar (Comportamiento Upsert).")

    # 5. TEST: Cambiar estado a producto que no existe
    print("\n[ERROR TEST 5] Patch de estado a ID inválido...")
    res = requests.patch(f"{BASE_URL}/8888/estado", json={
        "id_usuario": ID_USUARIO,
        "activo": False
    })
    if res.status_code == 404:
        print(f"   [OK] Producto no encontrado manejado correctamente.")
    else:
        print(f"   [FALLO] Se esperaba 404.")

def probar_flujo_limpio():
    print("\n--- TEST DE FLUJO EXITOSO (CATEGORÍA NUEVA) ---")
    # Crear categoría limpia para pruebas
    res_cat = requests.post(f"{BASE_URL}/categorias", json={
        "id_usuario": ID_USUARIO,
        "nombre": "Promociones"
    })
    cat_id = res_cat.json().get('id')
    
    # Crear producto en esa categoría
    res_prod = requests.post(f"{BASE_URL}/gestionar", json={
        "id_usuario": ID_USUARIO,
        "nombre_producto": "Promo Real",
        "precio_producto": 9990,
        "categoria_id": cat_id
    })
    if res_prod.status_code == 200:
        print(f"   [OK] Flujo completo exitoso en categoría {cat_id}.")

if __name__ == "__main__":
    test_productos_blindaje()
    probar_flujo_limpio()
