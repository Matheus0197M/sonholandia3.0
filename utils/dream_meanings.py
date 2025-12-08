"""API para buscar significados de sonhos usando cache e API externa"""
import logging
import requests
from functools import lru_cache
from models import get_db

logger = logging.getLogger(__name__)

# Base de dados local de significados (para fallback rápido)
DREAM_MEANINGS_LOCAL = {
    'voar': 'Sonhar que está voando geralmente representa liberdade, ambição e desejo de escapar das limitações. Pode indicar elevação espiritual ou fuga de problemas.',
    'cair': 'Queda em sonhos simboliza perda de controle, insegurança ou ansiedade. Pode representar medo de fracasso ou sensação de vulnerabilidade.',
    'morte': 'Morte em sonhos não é literal. Representa transformação, fim de um ciclo, mudança ou transição importante na vida.',
    'água': 'Água em sonhos representa emoções, inconsistência e fluidez. Água calma = paz, turbulenta = emoções instáveis.',
    'casa': 'Casa representa o eu interior, segurança e lar. Explorar uma casa = autodescoberta. Casa abandonada = partes de si desconectadas.',
    'perseguição': 'Ser perseguido em sonhos indica fuga de conflitos ou emoções reprimidas. Medo de enfrentar algo na vida real.',
    'sexo': 'Sonhos sexuais não são literais. Podem representar conexão, energia criativa, poder ou desejo de intimidade emocional.',
    'morte de alguém': 'Morte de outro em sonhos não prediz morte real. Representa mudança naquela relação ou fim de um padrão.',
    'dente caindo': 'Queda de dentes é associada a ansiedade, transição de vida ou perda. Também pode indicar mudanças positivas.',
    'animais': 'Animais em sonhos representam instintos e características. Cachorro = lealdade, gato = independência, serpente = transformação.',
    'sangue': 'Sangue pode representar energia vital, traição, culpa ou paixão. Contexto determina significado exato.',
    'fogo': 'Fogo representa transformação, paixão e destruição/renovação. Pode indicar raiva reprimida ou energia criativa.',
    'dinheiro': 'Dinheiro em sonhos = valor pessoal, poder ou segurança. Encontrar dinheiro = descoberta, perder = insegurança.',
    'comida': 'Comida representa nutrição emocional, desejo ou necessidade. Tipo de comida pode revelar o que você precisa emocionalmente.',
    'escola': 'Escola representa aprendizado, avaliação ou ansiedade. Pode indicar foco em desenvolvimento pessoal ou medo de julgamento.',
    'amigo': 'Amigos em sonhos representam partes de si ou relações. Ação do amigo no sonho é importante para interpretação.',
    'inimigo': 'Inimigos em sonhos frequentemente representam aspectos rejeitados de si mesmo, não a pessoa real.',
    'viagem': 'Viagem simboliza jornada de vida, mudança ou busca por algo. Destino e modo de transporte têm significado.',
    'família': 'Membros da família em sonhos representam papéis familiares e dinâmicas. Também podem representar partes de si.',
}

@lru_cache(maxsize=200)
def get_dream_meaning(dream_word: str, lang: str = 'pt') -> dict:
    """
    Busca significado de um sonho usando cache local primeiro, depois API.
    
    Args:
        dream_word: Palavra/tema do sonho (ex: 'voar', 'água')
        lang: Idioma (pt, en, es)
    
    Returns:
        {
            'word': str,
            'meaning': str,
            'source': str,  # 'local' ou 'api'
            'language': str
        }
    """
    dream_word = dream_word.lower().strip()
    
    if not dream_word:
        return {'word': '', 'meaning': 'Palavra inválida', 'source': 'error', 'language': lang}
    
    # Tenta obter do cache local primeiro (mais rápido)
    if dream_word in DREAM_MEANINGS_LOCAL:
        meaning = DREAM_MEANINGS_LOCAL[dream_word]
        
        # Traduz se necessário
        if lang != 'pt':
            try:
                from utils.translator import translate_text
                meaning = translate_text(meaning, lang, 'pt')
            except:
                pass
        
        return {
            'word': dream_word,
            'meaning': meaning,
            'source': 'local',
            'language': lang
        }
    
    # Tenta buscar de API externa (fallback)
    try:
        # Usando uma API gratuita de significados de sonhos
        # Alternativa: https://rapidapi.com/laxmanprabhakar/api/dream-interpretation-api
        result = _fetch_from_dream_api(dream_word, lang)
        if result:
            return result
    except Exception as e:
        logger.error(f"Erro ao buscar significado da API: {e}")
    
    # Fallback: retorna mensagem genérica
    return {
        'word': dream_word,
        'meaning': f'Significado de "{dream_word}" não encontrado. Tente outras palavras-chave relacionadas ao seu sonho.',
        'source': 'fallback',
        'language': lang
    }


def _fetch_from_dream_api(word: str, lang: str) -> dict:
    """
    Busca significado de uma API externa (implementação de fallback).
    Usa APIs gratuitas disponíveis.
    """
    try:
        # Opção 1: Dream API gratuita do RapidAPI (requer chave, deixar comentado)
        # url = f"https://laxmanprabhakar-dream-interpretation-api.p.rapidapi.com/{word}"
        # headers = {
        #     "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        #     "X-RapidAPI-Host": "laxmanprabhakar-dream-interpretation-api.p.rapidapi.com"
        # }
        # response = requests.get(url, headers=headers, timeout=5)
        # if response.status_code == 200:
        #     data = response.json()
        #     meaning = data.get('interpretations', [{}])[0].get('interpretation', '')
        
        # Por enquanto, retorna None para usar cache local
        return None
    except:
        return None


def save_dream_meaning_cache(dream_id: int, word: str, meaning: str, language: str = 'pt'):
    """
    Salva significado em cache no banco para reduzir requisições à API.
    
    Args:
        dream_id: ID do sonho
        word: Palavra do significado
        meaning: Significado em texto
        language: Idioma do significado
    """
    try:
        # Implementar tabela 'dream_meanings_cache' no banco de dados futuramente
        # Por enquanto, apenas log
        logger.info(f"Cache de significado para sonho {dream_id}, palavra '{word}' em {language}")
    except Exception as e:
        logger.error(f"Erro ao salvar cache de significado: {e}")


def get_keywords_from_dream(dream_text: str) -> list:
    """
    Extrai palavras-chave de um texto de sonho para buscar significados.
    
    Args:
        dream_text: Texto do sonho
    
    Returns:
        Lista de palavras-chave
    """
    # Palavras comuns a filtrar (stopwords em português)
    stopwords = {'o', 'a', 'de', 'para', 'com', 'em', 'que', 'e', 'é', 'do', 'da', 
                 'ou', 'na', 'no', 'um', 'uma', 'os', 'as', 'dos', 'das', 'por', 'foi', 
                 'seja', 'seu', 'sua', 'como', 'se', 'não', 'ele', 'ela', 'eu', 'eu'}
    
    # Tokeniza e filtra
    words = dream_text.lower().split()
    keywords = [
        word.strip('.,!?;:') 
        for word in words 
        if word.strip('.,!?;:') not in stopwords and len(word) > 3
    ]
    
    # Remove duplicatas mantendo ordem
    seen = set()
    unique = []
    for w in keywords:
        if w not in seen:
            unique.append(w)
            seen.add(w)
    
    return unique[:5]  # Retorna até 5 palavras-chave
