from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.usuario import Usuario
from app.models.cita import Cita
from app.models.servicio import Servicio
from app.models.multa import Multa
from app.models.reporte import ReporteMensual
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Bienvenido al panel de administración', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Contraseña incorrecta', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Sesión de admin cerrada', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    hoy = datetime.now()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    
    citas_mes = Cita.query.filter(
        Cita.fecha >= inicio_mes.date(),
        Cita.estado != 'cancelada'
    ).all()
    
    total_citas = len(citas_mes)
    asistieron = len([c for c in citas_mes if c.estado == 'asistió'])
    no_asistieron = len([c for c in citas_mes if c.estado == 'no_asistió'])
    pendientes = len([c for c in citas_mes if c.estado == 'pendiente'])
    
    total_ingresos = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.pagado)
    total_contado = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.forma_pago == 'contado' and c.pagado)
    total_fiado = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.forma_pago == 'fiado' and c.pagado)
    fiado_pendiente = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.forma_pago == 'fiado' and not c.pagado)
    
    multas = Multa.query.filter(Multa.fecha_generacion >= inicio_mes).all()
    multas_cobradas = sum(m.monto for m in multas if m.pagada)
    multas_pendientes = sum(m.monto for m in multas if not m.pagada)
    
    servicio_mas_solicitado = db.session.query(
        Servicio.nombre, func.count(Cita.id_servicio)
    ).join(Cita).filter(
        Cita.fecha >= inicio_mes.date(),
        Cita.estado != 'cancelada'
    ).group_by(Servicio.nombre).order_by(func.count(Cita.id_servicio).desc()).first()
    
    return render_template('admin/dashboard.html',
        total_citas=total_citas,
        asistieron=asistieron,
        no_asistieron=no_asistieron,
        pendientes=pendientes,
        total_ingresos=total_ingresos,
        total_contado=total_contado,
        total_fiado=total_fiado,
        fiado_pendiente=fiado_pendiente,
        multas_cobradas=multas_cobradas,
        multas_pendientes=multas_pendientes,
        servicio_mas_solicitado=servicio_mas_solicitado[0] if servicio_mas_solicitado else 'Ninguno'
    )

@admin_bp.route('/citas')
def citas():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    citas = Cita.query.order_by(Cita.fecha.desc(), Cita.hora).all()
    return render_template('admin/citas.html', citas=citas)

@admin_bp.route('/cita/asistio/<int:cita_id>')
def cita_asistio(cita_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    cita = Cita.query.get_or_404(cita_id)
    cita.estado = 'asistió'
    cita.pagado = True if cita.forma_pago == 'contado' else cita.pagado
    db.session.commit()
    
    flash(f'Cita de {cita.usuario.nombre} marcada como ASISTIÓ', 'success')
    return redirect(url_for('admin.citas'))

@admin_bp.route('/cita/no-asistio/<int:cita_id>')
def cita_no_asistio(cita_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    cita = Cita.query.get_or_404(cita_id)
    cita.estado = 'no_asistió'
    db.session.commit()
    
    nueva_multa = Multa(
        id_usuario=cita.id_usuario,
        id_cita=cita.id,
        monto=100
    )
    db.session.add(nueva_multa)
    db.session.commit()
    
    flash(f'Cita de {cita.usuario.nombre} marcada como NO ASISTIÓ - Multa de $100 generada', 'danger')
    return redirect(url_for('admin.citas'))

@admin_bp.route('/cita/cambiar/<int:cita_id>')
def cita_cambiar(cita_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    cita = Cita.query.get_or_404(cita_id)
    estado_actual = cita.estado
    
    if estado_actual == 'asistió':
        cita.estado = 'pendiente'
        flash(f'Cita de {cita.usuario.nombre} cambiada a PENDIENTE', 'warning')
    elif estado_actual == 'no_asistió':
        multa = Multa.query.filter_by(id_cita=cita_id).first()
        if multa:
            db.session.delete(multa)
        cita.estado = 'pendiente'
        flash(f'Cita de {cita.usuario.nombre} cambiada a PENDIENTE - Multa eliminada', 'warning')
    elif estado_actual == 'pendiente':
        cita.estado = 'asistió'
        cita.pagado = True if cita.forma_pago == 'contado' else cita.pagado
        flash(f'Cita de {cita.usuario.nombre} cambiada a ASISTIÓ', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.citas'))

@admin_bp.route('/fiados')
def fiados():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    citas_fiadas = Cita.query.filter_by(
        forma_pago='fiado', 
        pagado=False, 
        estado='asistió'
    ).all()
    total_fiado = sum(c.servicio.precio for c in citas_fiadas)
    
    return render_template('admin/fiados.html', citas_fiadas=citas_fiadas, total_fiado=total_fiado)

@admin_bp.route('/fiado/cobrar/<int:cita_id>')
def fiado_cobrar(cita_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    cita = Cita.query.get_or_404(cita_id)
    cita.pagado = True
    cita.fecha_pago = datetime.utcnow()
    db.session.commit()
    
    flash(f'Fiado de {cita.usuario.nombre} cobrado exitosamente', 'success')
    return redirect(url_for('admin.fiados'))

@admin_bp.route('/multas')
def multas():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    multas = Multa.query.order_by(Multa.fecha_generacion.desc()).all()
    total_pendiente = sum(m.monto for m in multas if not m.pagada)
    total_cobrado = sum(m.monto for m in multas if m.pagada)
    
    return render_template('admin/multas.html', multas=multas, total_pendiente=total_pendiente, total_cobrado=total_cobrado)

@admin_bp.route('/multa/pagar/<int:multa_id>')
def multa_pagar(multa_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    multa = Multa.query.get_or_404(multa_id)
    multa.pagada = True
    multa.fecha_pago = datetime.utcnow()
    db.session.commit()
    
    flash(f'Multa de {multa.usuario.nombre} marcada como PAGADA', 'success')
    return redirect(url_for('admin.multas'))

@admin_bp.route('/multa/eliminar/<int:multa_id>')
def multa_eliminar(multa_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    multa = Multa.query.get_or_404(multa_id)
    usuario_nombre = multa.usuario.nombre
    db.session.delete(multa)
    db.session.commit()
    
    flash(f'Multa de {usuario_nombre} eliminada exitosamente', 'success')
    return redirect(url_for('admin.multas'))

@admin_bp.route('/reportes')
def reportes():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    meses = []
    for i in range(6):
        fecha = datetime.now() - timedelta(days=30*i)
        mes = fecha.month
        año = fecha.year
        
        inicio_mes = datetime(año, mes, 1)
        fin_mes = datetime(año, mes + 1, 1) if mes < 12 else datetime(año + 1, 1, 1)
        
        citas_mes = Cita.query.filter(
            Cita.fecha >= inicio_mes.date(), 
            Cita.fecha < fin_mes.date(),
            Cita.estado != 'cancelada'
        ).all()
        
        total_ingresos = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.pagado)
        total_contado = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.forma_pago == 'contado' and c.pagado)
        total_fiado = sum(c.servicio.precio for c in citas_mes if c.estado == 'asistió' and c.forma_pago == 'fiado' and c.pagado)
        
        meses.append({
            'mes': f'{mes:02d}/{año}',
            'total_ingresos': total_ingresos,
            'total_contado': total_contado,
            'total_fiado': total_fiado,
            'total_citas': len(citas_mes)
        })
    
    return render_template('admin/reportes.html', meses=meses)