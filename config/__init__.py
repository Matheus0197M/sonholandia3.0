"""Configurações da aplicação"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base da aplicação"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    DATABASE = os.getenv("DATABASE", "users.db")
    
    # OAuth Google
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    # OAuth Facebook
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
    FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")
    
    # Email (para recuperação de senha)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    
    # SSL/TLS
    SSL_VERIFY = os.getenv("SSL_VERIFY", "True").lower() == "true"

