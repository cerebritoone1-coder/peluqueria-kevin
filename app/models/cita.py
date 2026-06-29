from app import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    forma_pago = db.Column(db.String(10), nullable=False)
    pagado = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    servicio = db.relationship('Servicio', backref='citas', lazy=True)
    
    def __repr__(self):
        return f'<Cita {self.id} - {self.fecha} {self.hora}>'