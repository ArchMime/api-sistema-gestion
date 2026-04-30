from app import create_app
from app.models import db, Usuario, Categoria

app = create_app()

def seed():
    with app.app_context():
        # 1. Resetear la base de datos
        # Esto asegura que los IDs comiencen desde 1 y no haya basura de pruebas previas
        print("Borrando base de datos existente...")
        db.drop_all()
        
        print("Creando tablas nuevas...")
        db.create_all()

        # 2. Crear el Usuario Sistema (Será ID: 1 obligatoriamente)
        admin = Usuario(nombre="SISTEMA", rol="ADMIN", activo=True)
        db.session.add(admin)
        # Hacemos commit para asegurar que el ID 1 quede reservado antes de seguir
        db.session.commit()
        print(f"--- Usuario de Sistema creado (ID: {admin.id}) ---")

        # 3. Crear Trabajadores (Recibirán IDs: 2, 3 y 4)
        trabajadores = [
            {"nombre": "Persona A", "rol": "DUEÑO"},
            {"nombre": "Persona B", "rol": "COCINA"},
            {"nombre": "Persona C", "rol": "CAJA"}
        ]

        print("\nCreando trabajadores...")
        for t in trabajadores:
            nuevo = Usuario(nombre=t["nombre"], rol=t["rol"], activo=True)
            db.session.add(nuevo)
            print(f"Usuario {t['nombre']} añadido.")

        # 4. Crear Categorías base
        categorias = ["Almuerzos", "Bebidas", "Cafetería"]
        print("\nCreando categorías...")
        for cat_nom in categorias:
            nueva_cat = Categoria(nombre=cat_nom)
            db.session.add(nueva_cat)
            print(f"Categoría {cat_nom} añadida.")

        # Commit final para trabajadores y categorías
        db.session.commit()
        print("\n--- Base de datos lista para pruebas de funcionalidad ---")

if __name__ == '__main__':
    seed()
