"""Rotas principais da aplicação"""
from flask import render_template, session, redirect, url_for, request, jsonify
import json
import logging
from models import get_db
from utils.cache import cache_result
from . import main_bp

logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Página inicial (login)"""
    user = session.get('user')
    if user:
        return redirect(url_for('main.feed'))
    return render_template('index.html', user=user)

@main_bp.route('/feed')
def feed():
    """Página do feed"""
    user = session.get('user')
    if not user:
        return redirect(url_for('main.index'))
    
    # Busca sonhos do banco de dados
    conn = get_db()
    cursor = conn.cursor()
    
    # Filtros
    tag_filter = request.args.get('tag', '').strip()
    search_query = request.args.get('search', '').strip()
    filter_type = request.args.get('filter', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    # Query otimizada: JOIN com subqueries para contagens
    query = '''
        SELECT d.id, d.user_id, d.title, d.description, d.dream_type, d.tags, d.image_path,
               d.created_at, u.username, u.name, u.picture,
               (SELECT COUNT(*) FROM likes WHERE dream_id = d.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE dream_id = d.id AND user_id = ?) > 0 as is_liked,
               (SELECT COUNT(*) FROM favorites WHERE dream_id = d.id AND user_id = ?) > 0 as is_favorited
        FROM dreams d
        JOIN users u ON d.user_id = u.id
    '''
    params = [user['id'], user['id']]
    
    # Aplica filtros
    conditions = []
    
    if filter_type == 'liked':
        conditions.append('d.id IN (SELECT dream_id FROM likes WHERE user_id = ?)')
        params.insert(0, user['id'])
    elif filter_type == 'favorites':
        conditions.append('d.id IN (SELECT dream_id FROM favorites WHERE user_id = ?)')
        params.insert(0, user['id'])
    
    if tag_filter:
        conditions.append('d.tags LIKE ?')
        params.append(f'%"{tag_filter}"%')
    
    if search_query:
        conditions.append('(d.title LIKE ? OR d.description LIKE ?)')
        search_param = f'%{search_query}%'
        params.extend([search_param, search_param])
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    # Preserve parâmetros antes de adicionar LIMIT/OFFSET para a consulta de contagem
    params_for_count = list(params)

    query += ' ORDER BY d.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    try:
        cursor.execute(query, params)
    except Exception as e:
        # Em caso de erro na consulta do feed, evita quebrar o site
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao consultar sonhos para o feed: {e}")
        conn.close()
        return render_template('feed.html', user=user, dreams=[], tag_filter=tag_filter, search_query=search_query, filter_type=filter_type, page=page, total_pages=0)
    dreams = cursor.fetchall()
    
    # Conta total para paginação
    count_query = 'SELECT COUNT(*) as total FROM dreams d'
    if conditions:
        count_query += ' WHERE ' + ' AND '.join(conditions)
        count_params = params_for_count
    else:
        count_params = []

    try:
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
    except Exception:
        total = 0
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    
    # Processa tags para cada sonho
    dreams_list = []
    for dream in dreams:
        tags = []
        if dream['tags']:
            try:
                tags = json.loads(dream['tags'])
            except:
                tags = []
        
        dream_dict = dict(dream)
        dream_dict['tags_list'] = tags
        dreams_list.append(dream_dict)
    
    return render_template('feed.html', 
                         user=user, 
                         dreams=dreams_list, 
                         tag_filter=tag_filter,
                         search_query=search_query,
                         filter_type=filter_type,
                         page=page,
                         total_pages=total_pages)

@main_bp.route('/admin/reset-db', methods=['POST'])
def reset_database():
    """Rota administrativa para resetar o banco de dados completamente"""
    from models import reset_database as reset_db
    
    try:
        reset_db()
        return jsonify({'success': True, 'message': 'Banco de dados resetado com sucesso!'})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao resetar banco: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

