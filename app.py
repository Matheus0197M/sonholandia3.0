import os, logging
from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# carrega .env
load_dotenv()

# --- força requests/urllib3 a usar bundle de CA do certifi (útil em dev) ---
import certifi
os.environ.setdefault('REQUESTS_CA_BUNDLE', certifi.where())
os.environ.setdefault('SSL_CERT_FILE', certifi.where())

# logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# debug info
logger.debug("GOOGLE_CLIENT_ID=%s", os.getenv("GOOGLE_CLIENT_ID"))
logger.debug("OAUTH_REDIRECT_URI=%s", os.getenv("OAUTH_REDIRECT_URI"))

# configura OAuth (OpenID Connect)
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    try:
        redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
        if not redirect_uri:
            raise RuntimeError("OAUTH_REDIRECT_URI não configurado no .env")
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception:
        logger.exception("Erro ao iniciar o login com Google")
        return "Erro interno ao tentar logar (veja terminal).", 500

@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)
    session['user'] = {
        'id': userinfo.get('sub'),
        'name': userinfo.get('name'),
        'email': userinfo.get('email'),
        'picture': userinfo.get('picture'),
    }
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
