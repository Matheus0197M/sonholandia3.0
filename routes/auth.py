"""Rotas de autenticação"""
from flask import render_template, session, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from models import get_db, create_password_reset_token, validate_password_reset_token, mark_token_as_used
from utils.email_validator import is_email_valid
from config import Config
from . import auth_bp

logger = logging.getLogger(__name__)

@auth_bp.route('/loginNormal', methods=['GET', 'POST'])
def loginNormal():
    """Rota para login normal com formulário (usuário e senha)"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('main.index'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'id': user['id'],
                'name': user['name'] or user['username'],
                'email': user['email'],
                'username': user['username'],
                'picture': user['picture']
            }
            return redirect(url_for('main.feed'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
            return redirect(url_for('main.index'))
    
    return redirect(url_for('main.index'))
    """Rota para login automático (login de teste/demo)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', ('usuario_teste',))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (username, email, password, name) VALUES (?, ?, ?, ?)',
            ('usuario_teste', 'teste@sonholandia.com', generate_password_hash('123456'), 'Usuário Teste')
        )
        conn.commit()
        user_id = cursor.lastrowid
        session['user'] = {
            'id': user_id,
            'name': 'Usuário Teste',
            'email': 'teste@sonholandia.com',
            'username': 'usuario_teste',
            'picture': None
        }
    else:
        session['user'] = {
            'id': user['id'],
            'name': user['name'] or user['username'],
            'email': user['email'],
            'username': user['username'],
            'picture': user['picture']
        }
    
    conn.close()
    return redirect(url_for('main.feed'))

@auth_bp.route('/signUp', methods=['GET', 'POST'])
def signUp():
    """Rota para cadastro de novos usuários"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        name = request.form.get('name', '').strip()
        
        if not username or not email or not password:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('signup.html')
        
        # Valida email com mail.so
        api_key = Config.API_EMAIL_KEY
        is_valid, validation_msg = is_email_valid(email, api_key, allow_free=True, allow_temporary=False)
        if not is_valid:
            flash(f'Email inválido: {validation_msg}', 'error')
            return render_template('signup.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            if existing_user['username'] == username:
                flash('Este nome de usuário já está em uso.', 'error')
            else:
                flash('Este email já está cadastrado.', 'error')
            return render_template('signup.html')
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, email, password, name) VALUES (?, ?, ?, ?)',
                (username, email, hashed_password, name or username)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            session['user'] = {
                'id': user_id,
                'name': name or username,
                'email': email,
                'username': username,
                'picture': None
            }
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            conn.close()
            logger.error(f"Erro ao cadastrar usuário: {e}")
            flash('Erro ao realizar cadastro. Tente novamente.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@auth_bp.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    """Rota para solicitar reset de senha"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Por favor, informe seu email.', 'error')
            return render_template('forgot_password.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Cria token de reset
            token = create_password_reset_token(user['id'])
            
            # Em produção, aqui você enviaria um email com o link
            # Por enquanto, apenas mostra o token (apenas para desenvolvimento)
            reset_url = url_for('auth.resetPassword', token=token, _external=True)
            flash(f'Link de recuperação gerado! (Desenvolvimento: {reset_url})', 'info')
            logger.info(f"Token de reset criado para {email}: {token}")
        else:
            # Por segurança, não revela se o email existe ou não
            flash('Se o email existir, um link de recuperação será enviado.', 'info')
        
        return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')

@auth_bp.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    """Rota para resetar senha com token"""
    token_data = validate_password_reset_token(token)
    
    if not token_data:
        flash('Token inválido ou expirado. Solicite um novo link de recuperação.', 'error')
        return redirect(url_for('auth.forgotPassword'))
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Atualiza senha
        conn = get_db()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password, token_data['user_id'])
        )
        conn.commit()
        conn.close()
        
        # Marca token como usado
        mark_token_as_used(token)
        
        flash('Senha alterada com sucesso! Faça login com sua nova senha.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('reset_password.html', token=token)

@auth_bp.route('/logout')
def logout():
    """Rota para logout"""
    session.pop('user', None)
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/blog')
def blog():
    return render_template('blog.html')


@auth_bp.route('/about')
def about():
    return render_template('about.html')


@auth_bp.route('/terms')
def terms():
    return render_template('terms.html')


@auth_bp.route('/nossoApp')
def nossoApp():
    return render_template('nossoApp.html')

@auth_bp.route('/nossaIA')
def nossaIA():
    return render_template('nossaIA.html')

