from app import db
from app.models.cita import Cita
from datetime import datetime, timedelta

def verificar_disponibilidad(fecha, hora):
    """Verifica si un horario está disponible"""
    cita_existente = Cita.query.filter_by(
        fecha=fecha,
        hora=hora
    ).filter(Cita.estado != 'cancelada').first()
    
    return cita_existente is None

def obtener_horarios_disponibles(fecha):
    """Obtiene todos los horarios disponibles para una fecha"""
    horarios_todos = ['7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30']
    
    citas_ocupadas = Cita.query.filter_by(
        fecha=fecha
    ).filter(Cita.estado != 'cancelada').all()
    
    horarios_ocupados = [cita.hora for cita in citas_ocupadas]
    
    horarios_disponibles = [h for h in horarios_todos if h not in horarios_ocupados]
    
    return horarios_disponibles

def puede_cancelar(cita):
    """Verifica si una cita se puede cancelar (más de 1 hora antes)"""
    ahora = datetime.now()
    fecha_hora_cita = datetime.combine(cita.fecha, datetime.strptime(cita.hora, '%H:%M').time())
    diferencia = (fecha_hora_cita - ahora).total_seconds() / 3600
    
    return diferencia >= 1