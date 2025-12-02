"""Rotas da aplicação"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
dreams_bp = Blueprint('dreams', __name__)

# Importa as rotas para registrar os endpoints
from . import auth, main, oauth, newDream

