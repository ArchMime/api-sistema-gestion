from app import create_app
from app.models import db, Usuario, Categoria

app = create_app()

def seed():
    with app.app_context():
        # 1. Crear las tablas (si no existen)
        print("Creando tablas en la base de datos...")
        db.create_all()

        # 2. Crear el Usuario Sistema/Admin
        # Evitamos forzar el ID 0 y buscamos por nombre para que sea seguro re-ejecutar
        admin = Usuario.query.filter_by(nombre="SISTEMA").first()
        if not admin:
            # Dejamos que el ID sea autoincremental (será el 1)
            admin = Usuario(nombre="SISTEMA", rol="ADMIN", activo=True)
            db.session.add(admin)
            # Commit inmediato para asegurar la existencia del admin para lo que sigue
            db.session.commit()
            print(f"Usuario de Sistema creado (ID asignado: {admin.id}).")
        else:
            print("El usuario SISTEMA ya existe.")

        # 3. Crear Trabajadores (A, B y C)
        trabajadores = [
            {"nombre": "Persona A", "rol": "DUEÑO"},
            {"nombre": "Persona B", "rol": "COCINA"},
            {"nombre": "Persona C", "rol": "CAJA"}
        ]

        for t in trabajadores:
            if not Usuario.query.filter_by(nombre=t["nombre"]).first():
                nuevo = Usuario(nombre=t["nombre"], rol=t["rol"], activo=True)
                db.session.add(nuevo)
                print(f"Usuario {t['nombre']} creado.")
            else:
                print(f"Usuario {t['nombre']} ya existía.")

        # 4. Crear Categorías base (Parte no modificada)
        categorias = ["Almuerzos", "Bebidas", "Cafetería"]
        for cat_nom in categorias:
            if not Categoria.query.filter_by(nombre=cat_nom).first():
                db.session.add(Categoria(nombre=cat_nom))
                print(f"Categoría {cat_nom} creada.")
            else:
                print(f"Categoría {cat_nom} ya existía.")

        # Commit final para trabajadores y categorías
        db.session.commit()
        print("\n--- Base de datos lista para pruebas de funcionalidad ---")

if __name__ == '__main__':
    seed()
