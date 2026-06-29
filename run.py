from app import create_app, db
from app.models.usuario import Usuario
from app.models.servicio import Servicio
from app.models.cita import Cita
from app.models.multa import Multa
from app.models.reporte import ReporteMensual

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Usuario': Usuario, 
        'Servicio': Servicio, 
        'Cita': Cita, 
        'Multa': Multa,
        'ReporteMensual': ReporteMensual
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)