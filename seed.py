from app import create_app
from app.models import db, Usuario, Categoria

app = create_app()

def seed():
    with app.app_context():
        # Crea las tablas
        db.create_all()
        
        # 1. Crear Usuarios si no existen
        if not Usuario.query.first():
            u1 = Usuario(nombre="Persona A", rol="DUEÑO")
            u2 = Usuario(nombre="Persona B", rol="COCINA")
            u3 = Usuario(nombre="Persona C", rol="CAJA")
            db.session.add_all([u1, u2, u3])
            print("Usuarios A, B y C creados.")

        # 2. Crear Categorías base
        if not Categoria.query.first():
            c1 = Categoria(nombre="Almuerzos")
            c2 = Categoria(nombre="Bebidas")
            c3 = Categoria(nombre="Cafetería")
            db.session.add_all([c1, c2, c3])
            print("Categorías base creadas.")
            
        db.session.commit()
        print("Base de datos lista para trabajar.")

if __name__ == '__main__':
    seed()
