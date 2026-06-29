from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models.usuario import Usuario
from app.models.servicio import Servicio
from app.models.cita import Cita
from app.models.multa import Multa
from app.services.whatsapp import enviar_whatsapp
from datetime import datetime
import json

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    
    servicios = Servicio.query.all()
    horarios = ['7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30']
    
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        servicio_id = request.form.get('servicio_id')
        forma_pago = request.form.get('forma_pago')
        
        # Verificar si ya existe cita en ese horario
        cita_existente = Cita.query.filter_by(fecha=fecha, hora=hora).first()
        if cita_existente:
            flash('Este horario ya está ocupado. Por favor, elige otro.', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        # Obtener el usuario de la sesión
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario:
            flash('Usuario no encontrado. Por favor, inicia sesión nuevamente.', 'danger')
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Crear nueva cita
        nueva_cita = Cita(
            id_usuario=usuario.id,
            id_servicio=servicio_id,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            hora=hora,
            forma_pago=forma_pago,
            estado='pendiente'
        )
        db.session.add(nueva_cita)
        db.session.commit()
        
        # Obtener el servicio
        servicio = Servicio.query.get(servicio_id)
        if not servicio:
            flash('Servicio no encontrado', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        forma_pago_texto = "💰 Fiado (Crédito)" if forma_pago == "fiado" else "✅ Pagado de una vez (Contado)"
        
        mensaje = f"""🛎️ *NUEVA CITA - PELUQUERÍA* 💈

*Cliente:* {usuario.nombre}
*Teléfono:* {usuario.telefono}
*Fecha:* {fecha}
*Hora:* {hora}

✂️ *SERVICIO SOLICITADO:*
{servicio.nombre} → RD$ {servicio.precio:.2f}

💳 *FORMA DE PAGO:*
{forma_pago_texto}

⚠️ *POLÍTICAS:*
- Cancelación: hasta 1 hora antes
- Inasistencia: multa de RD$ 100

📅 Agendado: {datetime.now().strftime('%d/%m/%Y, %I:%M:%S %p')}"""
        
        enviar_whatsapp(mensaje)
        
        flash('¡Cita agendada exitosamente!', 'success')
        return redirect(url_for('cliente.mis_citas'))
    
    return render_template('cliente/agendar.html', servicios=servicios, horarios=horarios)

@cliente_bp.route('/mis-citas')
def mis_citas():
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    
    citas = Cita.query.filter_by(id_usuario=session['usuario_id']).order_by(Cita.fecha.desc()).all()
    multas = Multa.query.filter_by(id_usuario=session['usuario_id'], pagada=False).all()
    total_multas = sum(multa.monto for multa in multas)
    
    return render_template('cliente/mis_citas.html', citas=citas, total_multas=total_multas)

@cliente_bp.route('/cancelar-cita/<int:cita_id>')
def cancelar_cita(cita_id):
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    
    cita = Cita.query.get_or_404(cita_id)
    
    if cita.id_usuario != session['usuario_id']:
        flash('No autorizado', 'danger')
        return redirect(url_for('cliente.mis_citas'))
    
    ahora = datetime.now()
    fecha_hora_cita = datetime.combine(cita.fecha, datetime.strptime(cita.hora, '%H:%M').time())
    diferencia = (fecha_hora_cita - ahora).total_seconds() / 3600
    
    if diferencia < 1:
        flash('No se puede cancelar la cita. Solo se puede cancelar con 1 hora de antelación.', 'danger')
        return redirect(url_for('cliente.mis_citas'))
    
    cita.estado = 'cancelada'
    db.session.commit()
    
    flash('Cita cancelada exitosamente', 'success')
    return redirect(url_for('cliente.mis_citas'))

@cliente_bp.route('/horarios-disponibles')
def horarios_disponibles():
    fecha = request.args.get('fecha')
    if not fecha:
        return jsonify({'error': 'Fecha no proporcionada'}), 400
    
    # Obtener horarios ocupados para esa fecha
    citas_ocupadas = Cita.query.filter_by(fecha=fecha).filter(Cita.estado != 'cancelada').all()
    horarios_ocupados = [cita.hora for cita in citas_ocupadas]
    
    horarios_todos = ['7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30']
    horarios_disponibles = [h for h in horarios_todos if h not in horarios_ocupados]
    
    return jsonify({'disponibles': horarios_disponibles})