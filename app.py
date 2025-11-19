"""Aplicação principal Sonholândia"""
import logging
from flask import Flask

from config import Config
from models import init_db
from routes import auth_bp, main_bp
from routes.oauth import init_oauth, set_oauth
from utils import setup_ssl

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configura SSL
setup_ssl()

# Cria aplicação Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)

# Inicializa banco de dados
init_db()

# Inicializa OAuth
oauth = init_oauth(app)
set_oauth(oauth)

# Registra blueprints
app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(main_bp, url_prefix='')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
