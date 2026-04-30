class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos del Local (Para el encabezado y tickets)
    nombre_local = db.Column(db.String(100), default="Mi Negocio")
    direccion_local = db.Column(db.String(200), default="Calle Falsa 123") # <--- Nuevo
    leyenda_header = db.Column(db.String(255), default="Bienvenidos")
    logo_filename = db.Column(db.String(100), default="logo_default.png")
    
    # Personalización Visual
    color_principal = db.Column(db.String(7), default="#3498db")
    color_secundario = db.Column(db.String(7), default="#2ecc71")
    modo_oscuro = db.Column(db.Boolean, default=False) # <--- Útil para PWA
    
    # Preferencias Regionales
    moneda_simbolo = db.Column(db.String(5), default="$")
    tipo_fuente = db.Column(db.String(25), default="Roboto")
    tamanno_fuente = db.Column(db.Integer, default=14)
