import os
import re
import uuid
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from functools import wraps
from config import Config
from models import db, Usuario, Formulario, RespostaFormulario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

logger.info('Iniciando aplicacao Flask...')
logger.info(f'Database URL: {"configurada" if app.config["SQLALCHEMY_DATABASE_URI"] else "NAO CONFIGURADA"}')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def validar_senha(senha):
    if len(senha) < 8:
        return False
    if not re.search(r'[A-Za-z]', senha):
        return False
    if not re.search(r'[0-9]', senha):
        return False
    return True

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    logger.info(f'Access to / - user_authenticated: {current_user.is_authenticated}')
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f'Access to /login - method: {request.method}, user_authenticated: {current_user.is_authenticated}')
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        logger.info(f'Login attempt - email: {email}')
        
        if not email or not senha:
            logger.warning('Login failed - empty email or password')
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            logger.info(f'Login successful for user: {email}')
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f'Login failed - invalid credentials for email: {email}')
            flash('Email ou senha inválidos', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    logger.info(f'Access to /registro - method: {request.method}')
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        logger.info(f'Registro attempt - email: {email}')
        
        if not email or not senha or not confirmar_senha:
            logger.warning('Registro failed - empty fields')
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('registro.html')
        
        if not validar_email(email):
            flash('Email inválido', 'error')
            return render_template('registro.html')
        
        if not validar_senha(senha):
            logger.warning(f'Registro failed - invalid password for: {email}')
            flash('A senha deve ter pelo menos 8 dígitos com letras e números', 'error')
            return render_template('registro.html')
        
        if senha != confirmar_senha:
            logger.warning(f'Registro failed - passwords do not match for: {email}')
            flash('As senhas não conferem', 'error')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            logger.warning(f'Registro failed - email already exists: {email}')
            flash('Email já cadastrado', 'error')
            return render_template('registro.html')
        
        usuario = Usuario(email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        
        logger.info(f'User registered successfully: {email}')
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logger.info(f'User logged out: {current_user.email}')
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    logger.info(f'Dashboard accessed by: {current_user.email}')
    formularios = Formulario.query.filter_by(usuario_id=current_user.id).order_by(Formulario.created_at.desc()).all()
    return render_template('dashboard.html', formularios=formularios)

@app.route('/formulario/criar', methods=['GET', 'POST'])
@login_required
def criar_formulario():
    logger.info(f'Access /formulario/criar by: {current_user.email}')
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        
        if not nome:
            flash('Nome do formulário é obrigatório', 'error')
            return render_template('criar_formulario.html')
        
        link_unico = str(uuid.uuid4())
        
        formulario = Formulario(
            nome=nome,
            link_unico=link_unico,
            usuario_id=current_user.id
        )
        db.session.add(formulario)
        db.session.commit()
        
        logger.info(f'Formulario criado: {nome} (ID: {formulario.id})')
        flash(f'Formulário criado! Link: {request.host_url}formulario/{link_unico}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('criar_formulario.html')

@app.route('/formulario/<link_unico>', methods=['GET', 'POST'])
def responder_formulario(link_unico):
    logger.info(f'Access /formulario/{link_unico} - method: {request.method}')
    
    formulario = Formulario.query.filter_by(link_unico=link_unico).first_or_404()
    
    if request.method == 'POST':
        dados = request.get_json()
        
        nome = dados.get('nome', '').strip()
        email = dados.get('email', '').strip()
        data_nascimento = dados.get('data-nascimento', '').strip()
        telefone = dados.get('telefone', '').strip()
        
        if not nome or not email or not data_nascimento or not telefone:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        
        resposta = RespostaFormulario(
            formulario_id=formulario.id,
            dados={
                'nome': nome,
                'email': email,
                'data_nascimento': data_nascimento,
                'telefone': telefone
            }
        )
        db.session.add(resposta)
        db.session.commit()
        
        logger.info(f'Resposta recebida para formulario ID: {formulario.id}')
        return jsonify({'mensagem': 'Formulário salvo com sucesso!'})
    
    return render_template('formulario.html', formulario=formulario)

@app.route('/formulario/<int:id>/respostas')
@login_required
def ver_respostas(id):
    logger.info(f'Access /formulario/{id}/respostas by: {current_user.email}')
    formulario = Formulario.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    respostas = RespostaFormulario.query.filter_by(formulario_id=id).order_by(RespostaFormulario.created_at.desc()).all()
    return render_template('respostas.html', formulario=formulario, respostas=respostas)

@app.route('/formulario/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_formulario(id):
    formulario = Formulario.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    logger.info(f'Excluindo formulario ID: {id} - {formulario.nome}')
    db.session.delete(formulario)
    db.session.commit()
    flash('Formulário excluído com sucesso', 'success')
    return redirect(url_for('dashboard'))

@app.route('/resposta/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_resposta(id):
    resposta = RespostaFormulario.query.get_or_404(id)
    formulario = Formulario.query.filter_by(id=resposta.formulario_id, usuario_id=current_user.id).first_or_404()
    logger.info(f'Excluindo resposta ID: {id} do formulario ID: {formulario.id}')
    db.session.delete(resposta)
    db.session.commit()
    flash('Resposta excluída com sucesso', 'success')
    return redirect(url_for('ver_respostas', id=formulario.id))

if __name__ == '__main__':
    logger.info('Iniciando servidor Flask...')
    with app.app_context():
        db.create_all()
    logger.info('Banco de dados准备好了 (tabelas criadas)')
    app.run(debug=True)