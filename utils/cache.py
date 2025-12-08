"""Utilidades de cache e performance"""
import logging
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache em memória para reduzir queries ao banco
_memory_cache = {}
_cache_timestamps = {}

CACHE_DURATION = {
    'user': 3600,           # 1 hora
    'dream': 600,           # 10 minutos
    'dream_list': 300,      # 5 minutos
    'stats': 900,           # 15 minutos
    'tags': 3600,           # 1 hora
}


def cache_result(cache_key_prefix: str, duration: int = 300):
    """
    Decorador para cachear resultados de funções.
    
    Args:
        cache_key_prefix: Prefixo da chave de cache
        duration: Duração em segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cria chave de cache única
            cache_key = f"{cache_key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Verifica se existe no cache e se ainda é válido
            if cache_key in _memory_cache:
                timestamp = _cache_timestamps.get(cache_key)
                if timestamp and (datetime.now() - timestamp).total_seconds() < duration:
                    logger.debug(f"Cache hit: {cache_key}")
                    return _memory_cache[cache_key]
            
            # Executa função
            result = func(*args, **kwargs)
            
            # Armazena em cache
            _memory_cache[cache_key] = result
            _cache_timestamps[cache_key] = datetime.now()
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: str = None):
    """Limpa cache em memória"""
    global _memory_cache, _cache_timestamps
    
    if pattern:
        keys_to_delete = [k for k in _memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del _memory_cache[key]
            if key in _cache_timestamps:
                del _cache_timestamps[key]
        logger.info(f"Cache limpo: {len(keys_to_delete)} entradas removidas")
    else:
        _memory_cache.clear()
        _cache_timestamps.clear()
        logger.info("Cache completamente limpo")


def get_cache_stats():
    """Retorna estatísticas do cache"""
    return {
        'total_entries': len(_memory_cache),
        'memory_usage_kb': sum(len(str(v)) for v in _memory_cache.values()) / 1024
    }
