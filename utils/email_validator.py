"""Validação de email usando mail.so API"""
import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache de validações para não sobrecarregar API (máx 100 emails em memória)
@lru_cache(maxsize=100)
def validate_email_with_mailso(email: str, api_key: str = None) -> dict:
    """
    Valida email usando mail.so API.
    
    Args:
        email: Email a validar
        api_key: API key do mail.so (obrigatório)
    
    Returns:
        {
            'valid': bool,
            'reason': str,
            'is_temporary': bool,
            'is_disposable': bool,
            'is_free_email': bool
        }
    """
    if not api_key:
        # Se não houver API key, retorna validação básica
        return {
            'valid': bool('@' in email and '.' in email.split('@')[1]),
            'reason': 'basic_validation',
            'is_temporary': False,
            'is_disposable': False,
            'is_free_email': False
        }
    
    try:
        # Endpoint da mail.so API
        url = f"https://api.mail.so/verify"
        headers = {'Authorization': f'Bearer {api_key}'}
        params = {'email': email}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'valid': data.get('valid', False),
            'reason': data.get('reason', 'unknown'),
            'is_temporary': data.get('is_temporary', False),
            'is_disposable': data.get('is_disposable', False),
            'is_free_email': data.get('is_free_email', False)
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao validar email com mail.so: {e}")
        # Retorna True por padrão se API falhar (não bloqueia signup)
        return {
            'valid': True,
            'reason': 'api_error',
            'is_temporary': False,
            'is_disposable': False,
            'is_free_email': False
        }


def is_email_valid(email: str, api_key: str = None, allow_free: bool = True, 
                   allow_temporary: bool = False) -> tuple[bool, str]:
    """
    Valida email com critérios customizáveis.
    
    Args:
        email: Email a validar
        api_key: API key do mail.so
        allow_free: Permitir emails de provedores gratuitos (Gmail, Yahoo, etc)
        allow_temporary: Permitir emails temporários (10minutemail, etc)
    
    Returns:
        (is_valid: bool, message: str)
    """
    # Validação básica de formato
    if not email or '@' not in email:
        return False, "Email inválido"
    
    if len(email) > 254:
        return False, "Email muito longo"
    
    # Validação com API
    result = validate_email_with_mailso(email, api_key)
    
    if not result['valid']:
        return False, f"Email inválido: {result['reason']}"
    
    if result['is_temporary'] and not allow_temporary:
        return False, "Emails temporários não são permitidos"
    
    if result['is_disposable'] and not allow_temporary:
        return False, "Emails descartáveis não são permitidos"
    
    if result['is_free_email'] and not allow_free:
        return False, "Emails de provedores gratuitos não são permitidos"
    
    return True, "Email válido"
