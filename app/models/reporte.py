from app import db
from datetime import datetime

class ReporteMensual(db.Model):
    __tablename__ = 'reportes_mensuales'
    
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    año = db.Column(db.Integer, nullable=False)
    total_ingresos = db.Column(db.Float, default=0)
    total_contado = db.Column(db.Float, default=0)
    total_fiado = db.Column(db.Float, default=0)
    total_fiado_cobrado = db.Column(db.Float, default=0)
    total_fiado_pendiente = db.Column(db.Float, default=0)
    total_multas = db.Column(db.Float, default=0)
    total_multas_cobradas = db.Column(db.Float, default=0)
    total_multas_pendientes = db.Column(db.Float, default=0)
    total_citas = db.Column(db.Integer, default=0)
    total_asistieron = db.Column(db.Integer, default=0)
    total_no_asistieron = db.Column(db.Integer, default=0)
    total_pendientes = db.Column(db.Integer, default=0)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reporte {self.mes}/{self.año}>'