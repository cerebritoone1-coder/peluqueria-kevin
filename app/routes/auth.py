from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.usuario import Usuario
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('cliente.agendar'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        
        usuario_existente = Usuario.query.filter_by(telefono=telefono).first()
        if usuario_existente:
            flash('Este número de teléfono ya está registrado', 'danger')
            return redirect(url_for('auth.registro'))
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            telefono=telefono
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        session['usuario_id'] = nuevo_usuario.id
        session['usuario_nombre'] = nuevo_usuario.nombre
        session['usuario_telefono'] = nuevo_usuario.telefono
        
        flash('¡Registro exitoso! Bienvenido a la peluquería', 'success')
        return redirect(url_for('cliente.agendar'))
    
    return render_template('cliente/registro.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        
        usuario = Usuario.query.filter_by(telefono=telefono).first()
        
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            session['usuario_telefono'] = usuario.telefono
            flash(f'Bienvenido de vuelta, {usuario.nombre}!', 'success')
            return redirect(url_for('cliente.agendar'))
        else:
            flash('Número de teléfono no registrado. Por favor, regístrate.', 'danger')
            return redirect(url_for('auth.registro'))
    
    return render_template('cliente/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('auth.login'))