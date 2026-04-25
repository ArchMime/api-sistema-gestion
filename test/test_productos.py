import requests

# URLs basadas en tu app/__init__.py
BASE_URL = "http://127.0.0.1:5000/api/productos"
ID_USUARIO = 3  # Persona B (Cocina)

def probar_productos():
    print("--- INICIANDO TEST DE PRODUCTOS EN LA TABLET ---")

    # 1. Crear Categoría
    print("\n1. Creando categoría 'Sandwich'...")
    res_cat = requests.post(f"{BASE_URL}/categorias", json={
        "id_usuario": ID_USUARIO,
        "nombre": "Sandwich"
    })
    
    if res_cat.status_code == 201:
        id_cat = res_cat.json().get('id')
        print(f"   [OK] Categoría creada ID: {id_cat}")
    else:
        print(f"   [ERROR] {res_cat.text}")
        return

    # 2. Crear Producto
    print("\n2. Creando producto 'Ave Mayo'...")
    res_prod = requests.post(f"{BASE_URL}/gestionar", json={
        "id_usuario": ID_USUARIO,
        "nombre_producto": "Ave Mayo",
        "precio_producto": 3500,
        "categoria_id": id_cat,
        "formato_producto": "Pan de molde"
    })
    
    if res_prod.status_code == 200:
        cod_prod = res_prod.json().get('id')
        print(f"   [OK] Producto creado Código: {cod_prod}")
    else:
        print(f"   [ERROR] {res_prod.text}")
        return

    # 3. Verificar en el Menú (PWA)
    print("\n3. Verificando visibilidad en /menu...")
    res_menu = requests.get(f"{BASE_URL}/menu")
    menu = res_menu.json()
    
    encontrado = any(p['id'] == cod_prod for cat in menu for p in cat['productos'])
    print(f"   [OK] ¿Aparece en el menú?: {'SÍ' if encontrado else 'NO'}")

    # 4. Pausar producto (Temporada/Stock)
    print(f"\n4. Pausando producto {cod_prod}...")
    res_pausa = requests.patch(f"{BASE_URL}/{cod_prod}/estado", json={
        "id_usuario": ID_USUARIO,
        "activo": False
    })
    
    if res_pausa.status_code == 200:
        print("   [OK] Producto pausado correctamente.")
    
    # 5. Verificación final: No en menú, pero sí en catálogo maestro
    res_maestro = requests.get(f"{BASE_URL}/catalogo-maestro")
    en_maestro = any(p['id'] == cod_prod and p['activo'] == False for p in res_maestro.json())
    print(f"   [OK] ¿Persiste inactivo en Catálogo Maestro?: {'SÍ' if en_maestro else 'NO'}")

if __name__ == "__main__":
    probar_productos()
