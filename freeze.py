from flask_frozen import Freezer
from app import create_app
from flask import url_for
app = create_app()
freezer = Freezer(app)
# Generador de URLs que excluye rutas con parámetros
@freezer.register_generator
def url_generator():
    # Lista de rutas que quieres congelar (sin parámetros)
    rutas = [
        '/',
        '/auth/registro',
        '/auth/login',
        '/auth/logout',
        '/cliente/agendar',
        '/cliente/mis-citas',
        '/admin/login',
        '/admin/dashboard',
        '/admin/citas',
        '/admin/fiados',
        '/admin/multas',
        '/admin/reportes',
    ]
    for ruta in rutas:
        yield {'path': ruta}
if __name__ == '__main__':
    freezer.freeze()
