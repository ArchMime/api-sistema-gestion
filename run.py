from app import create_app
from app.models import db
import os

# Creamos la instancia de la app
app = create_app()

if __name__ == '__main__':
    # Creamos las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
        print("Base de datos verificada/creada.")

    # Interruptor de modo: cambia a False para usar Waitress (Producción)
    modo_desarrollo = True 

    if modo_desarrollo:
        print("Iniciando en modo DESARROLLO (Debug: ON)...")
        # debug=True permite el auto-reload al guardar archivos
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from waitress import serve
        print("Iniciando en modo PRODUCCIÓN (Waitress)...")
        # El host 0.0.0.0 es vital para que se vea en la red del celular
        serve(app, host='0.0.0.0', port=5000)

