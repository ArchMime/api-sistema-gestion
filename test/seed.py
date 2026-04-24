from app import create_app
from app.models import db, Usuario, Categoria

app = create_app()

def seed():
    with app.app_context():
        # Crea las tablas (basado en tus modelos actualizados)
        db.create_all()
        
        # 1. Crear el Usuario Sistema/Admin (ID 0 o ID 1 para auditoría)
        # Es vital que exista un "ancla" para las acciones del servidor
        admin = Usuario.query.filter_by(id=0).first()
        if not admin:
            # Forzamos el ID 0 si tu DB lo permite, o simplemente el primer registro
            admin = Usuario(id=0, nombre="SISTEMA", rol="ADMIN", activo=True)
            db.session.add(admin)
            # Hacemos commit inmediato para que los siguientes usuarios 
            # puedan ser auditados si fuera necesario
            db.session.commit()
            print("Usuario de Sistema (ID 0) creado para auditorías.")

        # 2. Crear Trabajadores (A, B y C)
        # Usamos filter_by por nombre para que el seed sea seguro de re-ejecutar
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

        # 3. Crear Categorías base
        categorias = ["Almuerzos", "Bebidas", "Cafetería"]
        for cat_nom in categorias:
            if not Categoria.query.filter_by(nombre=cat_nom).first():
                db.session.add(Categoria(nombre=cat_nom))
                print(f"Categoría {cat_nom} creada.")
            
        db.session.commit()
        print("Base de datos lista para pruebas de funcionalidad.")

if __name__ == '__main__':
    seed()

