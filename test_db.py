from app import create_app
from app.models import db
from app.models.producto import Categoria, Producto

app = create_app()

with app.app_context():
    # 1. Crear las tablas (solo si no existen)
    db.create_all()
    
    # 2. Crear datos de prueba
    cat = Categoria(nombre="Bebidas")
    db.session.add(cat)
    db.session.commit()
    
    # 3. Consultar y mostrar
    print(Categoria.query.all())
