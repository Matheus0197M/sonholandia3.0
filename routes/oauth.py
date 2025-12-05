"""Rotas de OAuth (Google e Facebook)"""
from flask import redirect, url_for, session, flash, render_template_string
from authlib.integrations.flask_client import OAuth
import logging
import time
import threading

from config import Config
from models import get_db
from werkzeug.security import generate_password_hash
from . import auth_bp
from .oauthGoogle import start_flet_oauth, get_oauth_user_data, reset_oauth_state

logger = logging.getLogger(__name__)

def init_oauth(app):
    """Inicializa OAuth com Google e Facebook"""
    oauth = OAuth(app)
    
    # Google OAuth
    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET:
        try:
            oauth.register(
                name='google',
                client_id=Config.GOOGLE_CLIENT_ID,
                client_secret=Config.GOOGLE_CLIENT_SECRET,
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                client_kwargs={'scope': 'openid email profile'}
            )
            logger.info("OAuth Google configurado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao configurar OAuth Google: {e}")
    else:
        logger.warning("Credenciais do Google OAuth não encontradas no .env")
    
    # Facebook OAuth
    if Config.FACEBOOK_CLIENT_ID and Config.FACEBOOK_CLIENT_SECRET:
        try:
            oauth.register(
                name='facebook',
                client_id=Config.FACEBOOK_CLIENT_ID,
                client_secret=Config.FACEBOOK_CLIENT_SECRET,
                server_metadata_url='https://www.facebook.com/.well-known/openid-configuration',
                client_kwargs={'scope': 'email'}
            )
            logger.info("OAuth Facebook configurado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao configurar OAuth Facebook: {e}")
    else:
        logger.warning("Credenciais do Facebook OAuth não encontradas no .env")
    
    return oauth

oauth = None

def set_oauth(oauth_instance):
    """Define a instância do OAuth"""
    global oauth
    oauth = oauth_instance

@auth_bp.route('/loginWithGoogle')
def loginWithGoogle():
    """Rota para iniciar login com Google OAuth usando Flet"""
    try:
        # Reseta o estado anterior
        reset_oauth_state()
        
        # Inicia o servidor Flet OAuth
        thread = start_flet_oauth()
        
        # Retorna uma página de loading que verifica o status do login
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login com Google - Sonholândia</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .error-message {
                    color: #d32f2f;
                    margin-top: 20px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Conectando com Google...</h2>
                <div class="spinner"></div>
                <p>Aguarde enquanto abrimos a janela de login do Google.</p>
                <p><small>Se a janela não abrir automaticamente, <a href="http://localhost:8550" target="_blank">clique aqui</a></small></p>
                <div id="errorMessage" class="error-message" style="display: none;"></div>
            </div>
            <script>
                let checkCount = 0;
                const maxChecks = 60; // Máximo de 2 minutos (60 * 2 segundos)
                
                // Verifica o status a cada 2 segundos
                const checkInterval = setInterval(function() {
                    checkCount++;
                    
                    // Se exceder o tempo limite, para a verificação
                    if (checkCount > maxChecks) {
                        clearInterval(checkInterval);
                        const errorMsg = 'Login não disponível || Erro ao tentar logar';
                        document.getElementById('errorMessage').textContent = errorMsg;
                        document.getElementById('errorMessage').style.display = 'block';
                        setTimeout(function() {
                            window.location.href = '{{ url_for("auth.oauth_error") }}?error=' + encodeURIComponent(errorMsg);
                        }, 2000);
                        return;
                    }
                    
                    fetch('{{ url_for("auth.check_flet_oauth") }}')
                        .then(response => response.json())
                        .then(data => {
                            if (data.complete) {
                                clearInterval(checkInterval);
                                if (data.success) {
                                    window.location.href = '{{ url_for("main.feed") }}';
                                } else {
                                    // Exibe mensagem de erro antes de redirecionar
                                    const errorMsg = data.error || 'Login não disponível || Erro ao tentar logar';
                                    document.getElementById('errorMessage').textContent = errorMsg;
                                    document.getElementById('errorMessage').style.display = 'block';
                                    setTimeout(function() {
                                        window.location.href = '{{ url_for("auth.oauth_error") }}?error=' + encodeURIComponent(errorMsg);
                                    }, 2000);
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao verificar status:', error);
                            // Continua tentando mesmo com erro de rede
                        });
                }, 2000);
            </script>
        </body>
        </html>
        ''', url_for=url_for)
    except Exception as e:
        logger.error(f"Erro ao iniciar login com Google (Flet): {e}")
        flash('Login não disponível,ou, Erro ao tentar logar', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/check_flet_oauth')
def check_flet_oauth():
    """Verifica o status do login OAuth do Flet"""
    from flask import jsonify
    
    user_data, error, complete = get_oauth_user_data()
    
    if complete:
        if user_data:
            # Processa o login
            try:
                email = user_data.get('email')
                name = user_data.get('name')
                picture = user_data.get('picture')
                
                if not email:
                    reset_oauth_state()
                    return jsonify({
                        'complete': True,
                        'success': False,
                        'error': 'Login não disponível || Erro ao tentar logar'
                    })
                
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                
                username = None
                if not user:
                    # Cria novo usuário
                    username = email.split('@')[0]
                    base_username = username
                    counter = 1
                    while True:
                        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                        if not cursor.fetchone():
                            break
                        username = f"{base_username}{counter}"
                        counter += 1
                    
                    google_id = user_data.get('id', email)
                    cursor.execute(
                        'INSERT INTO users (username, email, password, name, picture) VALUES (?, ?, ?, ?, ?)',
                        (username, email, generate_password_hash(google_id), name, picture)
                    )
                    conn.commit()
                    user_id = cursor.lastrowid
                else:
                    user_id = user['id']
                    username = user['username']
                    if name and not user['name']:
                        cursor.execute('UPDATE users SET name = ?, picture = ? WHERE id = ?', (name, picture, user_id))
                        conn.commit()
                
                conn.close()
                
                # Cria a sessão
                session['user'] = {
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'picture': picture,
                    'username': username
                }
                
                # Reseta o estado
                reset_oauth_state()
                
                return jsonify({
                    'complete': True,
                    'success': True
                })
            except Exception as e:
                logger.error(f"Erro ao processar login Flet: {e}")
                reset_oauth_state()
                return jsonify({
                    'complete': True,
                    'success': False,
                    'error': 'Login não disponível || Erro ao tentar logar'
                })
        else:
            error_message = error or 'Login não disponível || Erro ao tentar logar'
            return jsonify({
                'complete': True,
                'success': False,
                'error': error_message
            })
    else:
        return jsonify({
            'complete': False,
            'success': False
        })

@auth_bp.route('/auth/google')
def auth_google():
    """Callback do Google OAuth"""
    if not oauth or 'google' not in oauth._clients:
        flash('Login com Google não está disponível no momento.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        token = oauth.google.authorize_access_token()
        userinfo = oauth.google.parse_id_token(token)
        
        email = userinfo.get('email')
        name = userinfo.get('name')
        picture = userinfo.get('picture')
        google_id = userinfo.get('sub')
        
        if not email:
            flash('Não foi possível obter o email do Google.', 'error')
            return redirect(url_for('main.index'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            username = email.split('@')[0]
            # Garante username único
            base_username = username
            counter = 1
            while True:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            cursor.execute(
                'INSERT INTO users (username, email, password, name, picture) VALUES (?, ?, ?, ?, ?)',
                (username, email, generate_password_hash(google_id), name, picture)
            )
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user['id']
            if name and not user['name']:
                cursor.execute('UPDATE users SET name = ?, picture = ? WHERE id = ?', (name, picture, user_id))
                conn.commit()
        
        conn.close()
        
        session['user'] = {
            'id': user_id,
            'name': name,
            'email': email,
            'picture': picture
        }
        flash('Login com Google realizado com sucesso!', 'success')
        return redirect(url_for('main.feed'))
    except Exception as e:
        logger.error(f"Erro no login com Google: {e}")
        flash('Erro ao fazer login com Google. Tente novamente.', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/loginWithFacebook')
def loginWithFacebook():
    """Rota para iniciar login com Facebook OAuth"""
    if not oauth or 'facebook' not in oauth._clients:
        flash('Login com Facebook não está disponível no momento.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        redirect_uri = Config.FACEBOOK_REDIRECT_URI or url_for('auth.auth_facebook', _external=True)
        return oauth.facebook.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Erro ao iniciar login com Facebook: {e}")
        flash('Erro ao conectar com Facebook. Tente novamente.', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/auth/facebook')
def auth_facebook():
    """Callback do Facebook OAuth"""
    if not oauth or 'facebook' not in oauth._clients:
        flash('Login com Facebook não está disponível no momento.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        token = oauth.facebook.authorize_access_token()
        resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture')
        userinfo = resp.json()
        
        email = userinfo.get('email')
        name = userinfo.get('name')
        picture = userinfo.get('picture', {}).get('data', {}).get('url') if userinfo.get('picture') else None
        facebook_id = userinfo.get('id')
        
        if not email:
            flash('Não foi possível obter o email do Facebook.', 'error')
            return redirect(url_for('main.index'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            username = email.split('@')[0]
            # Garante username único
            base_username = username
            counter = 1
            while True:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            cursor.execute(
                'INSERT INTO users (username, email, password, name, picture) VALUES (?, ?, ?, ?, ?)',
                (username, email, generate_password_hash(facebook_id), name, picture)
            )
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user['id']
            if name and not user['name']:
                cursor.execute('UPDATE users SET name = ?, picture = ? WHERE id = ?', (name, picture, user_id))
                conn.commit()
        
        conn.close()
        
        session['user'] = {
            'id': user_id,
            'name': name,
            'email': email,
            'picture': picture
        }
        flash('Login com Facebook realizado com sucesso!', 'success')
        return redirect(url_for('main.feed'))
    except Exception as e:
        logger.error(f"Erro no login com Facebook: {e}")
        flash('Erro ao fazer login com Facebook. Tente novamente.', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/oauth_error')
def oauth_error():
    """Rota intermediária para tratar erros do OAuth e exibir mensagem na página principal"""
    from flask import request
    error_message = request.args.get('error', 'Login não disponível,ou, Erro ao tentar logar')
    flash(error_message, 'error')
    return redirect(url_for('main.index'))

