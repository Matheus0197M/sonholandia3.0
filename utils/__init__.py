"""Utilitários da aplicação"""
import os
import certifi
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def setup_ssl():
    """Configura SSL/TLS para requisições"""
    os.environ.setdefault('REQUESTS_CA_BUNDLE', certifi.where())
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    
    # Desabilita avisos de SSL se necessário (apenas para desenvolvimento)
    # Em produção, sempre verificar certificados
    if os.getenv("SSL_VERIFY", "True").lower() == "false":
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session_with_retry():
    """Cria uma sessão HTTP com retry automático"""
    from requests import Session
    
    session = Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

