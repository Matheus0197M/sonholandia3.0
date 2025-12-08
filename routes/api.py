"""Rotas de API para funcionalidades interativas"""
from flask import jsonify, request, session
from models import get_db
from utils.dream_meanings import get_dream_meaning, get_keywords_from_dream
from utils.translator import get_text
from . import api_bp

@api_bp.route('/api/like', methods=['POST'])
def toggle_like():
    """API para curtir/descurtir um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    dream_id = data.get('dream_id')
    like = data.get('like', True)
    
    if not dream_id:
        return jsonify({'success': False, 'error': 'ID do sonho não fornecido'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if like:
            # Adiciona curtida
            cursor.execute('''
                INSERT OR IGNORE INTO likes (user_id, dream_id) 
                VALUES (?, ?)
            ''', (user['id'], dream_id))
        else:
            # Remove curtida
            cursor.execute('''
                DELETE FROM likes 
                WHERE user_id = ? AND dream_id = ?
            ''', (user['id'], dream_id))
        
        conn.commit()
        
        # Conta total de curtidas
        cursor.execute('SELECT COUNT(*) as count FROM likes WHERE dream_id = ?', (dream_id,))
        like_count = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'like_count': like_count
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    """API para favoritar/desfavoritar um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    dream_id = data.get('dream_id')
    favorite = data.get('favorite', True)
    
    if not dream_id:
        return jsonify({'success': False, 'error': 'ID do sonho não fornecido'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if favorite:
            # Adiciona favorito
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, dream_id) 
                VALUES (?, ?)
            ''', (user['id'], dream_id))
        else:
            # Remove favorito
            cursor.execute('''
                DELETE FROM favorites 
                WHERE user_id = ? AND dream_id = ?
            ''', (user['id'], dream_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/history', methods=['POST'])
def register_history():
    """API para registrar ações no histórico"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    dream_id = data.get('dream_id')
    action_type = data.get('action_type', 'view')
    
    if not dream_id:
        return jsonify({'success': False, 'error': 'ID do sonho não fornecido'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Remove histórico duplicado recente (mesma ação no mesmo sonho)
        cursor.execute('''
            DELETE FROM history 
            WHERE user_id = ? AND dream_id = ? AND action_type = ?
            AND created_at > datetime('now', '-1 hour')
        ''', (user['id'], dream_id, action_type))
        
        # Adiciona novo registro
        cursor.execute('''
            INSERT INTO history (user_id, dream_id, action_type)
            VALUES (?, ?, ?)
        ''', (user['id'], dream_id, action_type))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/comment', methods=['POST'])
def add_comment():
    """API para adicionar um comentário a um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    dream_id = data.get('dream_id')
    content = data.get('content', '').strip()
    
    if not dream_id:
        return jsonify({'success': False, 'error': 'ID do sonho não fornecido'}), 400
    
    if not content:
        return jsonify({'success': False, 'error': 'Conteúdo do comentário não fornecido'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verifica se o sonho existe
        cursor.execute('SELECT id FROM dreams WHERE id = ?', (dream_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Sonho não encontrado'}), 404
        
        # Adiciona comentário
        cursor.execute('''
            INSERT INTO comments (user_id, dream_id, content)
            VALUES (?, ?, ?)
        ''', (user['id'], dream_id, content))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/comments/<int:dream_id>', methods=['GET'])
def get_comments(dream_id):
    """API para obter comentários de um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT c.*, u.username, u.name, u.picture
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.dream_id = ?
            ORDER BY c.created_at ASC
        ''', (dream_id,))
        
        comments = cursor.fetchall()
        conn.close()
        
        comments_list = []
        for comment in comments:
            comments_list.append({
                'id': comment['id'],
                'content': comment['content'],
                'created_at': comment['created_at'],
                'username': comment['username'],
                'name': comment['name'],
                'picture': comment['picture']
            })
        
        return jsonify({
            'success': True,
            'comments': comments_list
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/api/dream-stats/<int:dream_id>', methods=['GET'])
def get_dream_stats(dream_id):
    """API para obter estatísticas de um sonho (curtidas, favoritos)"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verifica se o sonho existe
        cursor.execute('SELECT id FROM dreams WHERE id = ?', (dream_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Sonho não encontrado'}), 404
        
        # Conta curtidas
        cursor.execute('SELECT COUNT(*) as count FROM likes WHERE dream_id = ?', (dream_id,))
        like_count = cursor.fetchone()['count']
        
        # Verifica se o usuário curtiu
        cursor.execute('''
            SELECT COUNT(*) > 0 as is_liked 
            FROM likes 
            WHERE dream_id = ? AND user_id = ?
        ''', (dream_id, user['id']))
        is_liked = cursor.fetchone()['is_liked']
        
        # Verifica se o usuário favoritou
        cursor.execute('''
            SELECT COUNT(*) > 0 as is_favorited 
            FROM favorites 
            WHERE dream_id = ? AND user_id = ?
        ''', (dream_id, user['id']))
        is_favorited = cursor.fetchone()['is_favorited']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'like_count': like_count,
            'is_liked': bool(is_liked),
            'is_favorited': bool(is_favorited)
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/dream-meaning/<int:dream_id>', methods=['GET'])
def get_dream_meaning_api(dream_id):
    """API para obter significados de um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    # Parâmetro de idioma (padrão: português)
    lang = request.args.get('lang', 'pt').lower()
    if lang not in ['pt', 'en', 'es', 'fr', 'de']:
        lang = 'pt'
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Busca o sonho
        cursor.execute('SELECT title, description FROM dreams WHERE id = ?', (dream_id,))
        dream = cursor.fetchone()
        conn.close()
        
        if not dream:
            return jsonify({'success': False, 'error': 'Sonho não encontrado'}), 404
        
        # Extrai palavras-chave do título e descrição
        dream_text = f"{dream['title']} {dream['description']}"
        keywords = get_keywords_from_dream(dream_text)
        
        # Busca significados para cada palavra-chave
        meanings = []
        for keyword in keywords:
            meaning_data = get_dream_meaning(keyword, lang)
            if meaning_data and meaning_data['source'] != 'error':
                meanings.append(meaning_data)
        
        return jsonify({
            'success': True,
            'dream_id': dream_id,
            'keywords': keywords,
            'meanings': meanings,
            'language': lang
        })
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/dream-meaning/search', methods=['POST'])
def search_dream_meaning():
    """API para buscar significado de uma palavra específica"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    lang = data.get('language', 'pt').lower()
    
    if not word:
        return jsonify({'success': False, 'error': 'Palavra não fornecida'}), 400
    
    try:
        meaning_data = get_dream_meaning(word, lang)
        return jsonify({
            'success': True,
            **meaning_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


