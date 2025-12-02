"""Rotas principais da aplicação"""
from flask import render_template, session, redirect, url_for, request
import json
from models import get_db
from . import main_bp

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
    
    # Filtro por tag se fornecido
    tag_filter = request.args.get('tag', '').strip()
    
    if tag_filter:
        # Busca sonhos que contenham a tag
        cursor.execute('''
            SELECT d.*, u.username, u.name, u.picture 
            FROM dreams d
            JOIN users u ON d.user_id = u.id
            WHERE d.tags LIKE ?
            ORDER BY d.created_at DESC
            LIMIT 50
        ''', (f'%"{tag_filter}"%',))
    else:
        # Busca todos os sonhos
        cursor.execute('''
            SELECT d.*, u.username, u.name, u.picture 
            FROM dreams d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
            LIMIT 50
        ''')
    
    dreams = cursor.fetchall()
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
    
    return render_template('feed.html', user=user, dreams=dreams_list, tag_filter=tag_filter)

