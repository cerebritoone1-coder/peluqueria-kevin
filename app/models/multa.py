from app import db
from datetime import datetime

class Multa(db.Model):
    __tablename__ = 'multas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_cita = db.Column(db.Integer, db.ForeignKey('citas.id'), nullable=False)
    monto = db.Column(db.Float, default=100)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    pagada = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Multa {self.id} - ${self.monto}>'