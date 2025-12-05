"""Rotas de OAuth (Google e Facebook)"""
from flask import redirect, url_for, session, flash, render_template_string
from authlib.integrations.flask_client import OAuth
import logging

from config import Config
from models import get_db
from werkzeug.security import generate_password_hash
from . import auth_bp

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
    """Rota para iniciar login com Google OAuth"""
    if not oauth or 'google' not in oauth._clients:
        flash('Login com Google não está disponível no momento.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        redirect_uri = url_for('auth.auth_google', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Erro ao iniciar login com Google: {e}")
        flash('Erro ao conectar com Google. Tente novamente.', 'error')
        return redirect(url_for('main.index'))



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

