from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), unique=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    total_gastado = db.Column(db.Float, default=0)
    
    # Relaciones
    citas = db.relationship('Cita', backref='usuario', lazy=True)
    multas = db.relationship('Multa', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'