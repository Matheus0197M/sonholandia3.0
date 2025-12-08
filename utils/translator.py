"""Serviço de tradução usando Google Translate API (gratuito via google-translate-api)"""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Suporte de idiomas (código ISO 639-1)
SUPPORTED_LANGUAGES = {
    'pt': 'Português (Brasil)',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ja': 'Japanese',
    'zh': 'Chinese'
}

# Cache de traduções para reduzir requisições à API
_translation_cache = {}

def get_supported_languages():
    """Retorna dicionário de idiomas suportados"""
    return SUPPORTED_LANGUAGES


@lru_cache(maxsize=500)
def translate_text(text: str, target_language: str, source_language: str = 'pt') -> str:
    """
    Traduz texto usando google-translate-api (gratuito, sem API key).
    
    Args:
        text: Texto a traduzir
        target_language: Idioma alvo (ex: 'en', 'es')
        source_language: Idioma de origem (padrão: 'pt')
    
    Returns:
        Texto traduzido ou texto original se falhar
    """
    if not text or not text.strip():
        return text
    
    if target_language == source_language:
        return text
    
    # Tenta importar a biblioteca de tradução
    try:
        from google_translate_api import google_translate_api
        
        # Cache local para não fazer requisições repetidas
        cache_key = f"{text}_{source_language}_{target_language}"
        if cache_key in _translation_cache:
            return _translation_cache[cache_key]
        
        # Faz tradução
        result = google_translate_api.translate(
            text,
            target_language=target_language,
            source_language=source_language
        )
        
        translated = result.get('translatedText', text)
        
        # Armazena em cache
        _translation_cache[cache_key] = translated
        
        return translated
    
    except ImportError:
        logger.warning("google-translate-api não instalada. Usando fallback local.")
        return text
    except Exception as e:
        logger.error(f"Erro ao traduzir texto: {e}")
        return text


def get_translations_dict(lang: str = 'pt') -> dict:
    """
    Retorna dicionário de strings traduzidas para o idioma especificado.
    Usa cache local para evitar requisições repetidas.
    """
    # Dicionário base em português
    translations = {
        'pt': {
            'feed': 'Feed',
            'post_dream': 'Postar um sonho',
            'my_dreams': 'Meus Sonhos',
            'liked': 'Curtidos',
            'favorites': 'Favoritos',
            'history': 'Histórico',
            'logout': 'Sair',
            'search': 'Pesquisar',
            'see_more': 'Ver mais',
            'dream_meaning': 'Ver significado',
            'like': 'Curtir',
            'favorite': 'Favoritar',
            'comment': 'Comentar',
            'delete': 'Deletar',
            'edit': 'Editar',
            'back': 'Voltar',
            'send': 'Enviar',
            'cancel': 'Cancelar',
            'confirm': 'Confirmar',
            'error': 'Erro',
            'success': 'Sucesso',
            'loading': 'Carregando...',
            'no_dreams': 'Nenhum sonho encontrado',
            'no_dreams_with_tag': 'Nenhum sonho encontrado com a tag',
            'no_dreams_search': 'Nenhum sonho encontrado para',
        },
        'en': {
            'feed': 'Feed',
            'post_dream': 'Post a dream',
            'my_dreams': 'My Dreams',
            'liked': 'Liked',
            'favorites': 'Favorites',
            'history': 'History',
            'logout': 'Logout',
            'search': 'Search',
            'see_more': 'See more',
            'dream_meaning': 'See meaning',
            'like': 'Like',
            'favorite': 'Favorite',
            'comment': 'Comment',
            'delete': 'Delete',
            'edit': 'Edit',
            'back': 'Back',
            'send': 'Send',
            'cancel': 'Cancel',
            'confirm': 'Confirm',
            'error': 'Error',
            'success': 'Success',
            'loading': 'Loading...',
            'no_dreams': 'No dreams found',
            'no_dreams_with_tag': 'No dreams found with the tag',
            'no_dreams_search': 'No dreams found for',
        },
        'es': {
            'feed': 'Feed',
            'post_dream': 'Publicar un sueño',
            'my_dreams': 'Mis Sueños',
            'liked': 'Gustados',
            'favorites': 'Favoritos',
            'history': 'Historial',
            'logout': 'Cerrar sesión',
            'search': 'Buscar',
            'see_more': 'Ver más',
            'dream_meaning': 'Ver significado',
            'like': 'Gustó',
            'favorite': 'Favorito',
            'comment': 'Comentar',
            'delete': 'Eliminar',
            'edit': 'Editar',
            'back': 'Atrás',
            'send': 'Enviar',
            'cancel': 'Cancelar',
            'confirm': 'Confirmar',
            'error': 'Error',
            'success': 'Éxito',
            'loading': 'Cargando...',
            'no_dreams': 'No se encontraron sueños',
            'no_dreams_with_tag': 'No se encontraron sueños con la etiqueta',
            'no_dreams_search': 'No se encontraron sueños para',
        }
    }
    
    return translations.get(lang, translations['pt'])


def get_text(key: str, lang: str = 'pt', **kwargs) -> str:
    """
    Obtém texto traduzido por chave com fallback para português.
    
    Args:
        key: Chave do texto (ex: 'feed', 'like')
        lang: Idioma (ex: 'en', 'es')
        **kwargs: Valores para interpolação (ex: name='João')
    
    Returns:
        Texto traduzido
    """
    translations = get_translations_dict(lang)
    text = translations.get(key, translations.get(key, key))
    
    # Interpolação simples
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return text
