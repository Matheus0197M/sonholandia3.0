"""Rotas para postagem e visualização de sonhos"""
from flask import render_template, session, redirect, url_for, request, flash, jsonify
import logging
import time
import json

from models import get_db
from . import dreams_bp

logger = logging.getLogger(__name__)

@dreams_bp.route('/postar-sonho', methods=['GET', 'POST'])
def post_dream():
    """Rota para página de postagem de sonho"""
    user = session.get('user')
    if not user:
        flash('Você precisa estar logado para postar um sonho.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        dream_type = request.form.get('dream_type', '').strip()
        tags_input = request.form.get('tags', '').strip()
        
        # Validação
        if not title or not description or not dream_type:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('post_dream.html', user=user)
        
        # Processa tags (remove # e separa por vírgula ou espaço)
        tags_list = []
        if tags_input:
            # Remove # e separa por vírgula ou espaço
            tags_clean = tags_input.replace('#', '').replace(',', ' ')
            tags_list = [tag.strip().lower() for tag in tags_clean.split() if tag.strip()]
        
        # Salva no banco de dados
        conn = get_db()
        cursor = conn.cursor()
        try:
            tags_json = json.dumps(tags_list) if tags_list else None
            cursor.execute(
                'INSERT INTO dreams (user_id, title, description, dream_type, tags) VALUES (?, ?, ?, ?, ?)',
                (user['id'], title, description, dream_type, tags_json)
            )
            conn.commit()
            dream_id = cursor.lastrowid
            conn.close()
            
            # Redireciona para página de carregamento
            return redirect(url_for('dreams.loading_dream', dream_id=dream_id))
        except Exception as e:
            conn.close()
            logger.error(f"Erro ao salvar sonho: {e}")
            flash('Erro ao salvar o sonho. Tente novamente.', 'error')
            return render_template('post_dream.html', user=user)
    
    return render_template('post_dream.html', user=user)

@dreams_bp.route('/carregando-sonho/<int:dream_id>')
def loading_dream(dream_id):
    """Rota para página de carregamento enquanto o sonho é processado"""
    user = session.get('user')
    if not user:
        flash('Você precisa estar logado.', 'error')
        return redirect(url_for('main.index'))
    
    # Verifica se o sonho existe e pertence ao usuário
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dreams WHERE id = ? AND user_id = ?', (dream_id, user['id']))
    dream = cursor.fetchone()
    conn.close()
    
    if not dream:
        flash('Sonho não encontrado.', 'error')
        return redirect(url_for('main.feed'))
    
    return render_template('loading_dream.html', user=user, dream_id=dream_id)

@dreams_bp.route('/verificar-sonho/<int:dream_id>')
def check_dream(dream_id):
    """Rota AJAX para verificar se o sonho foi processado"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Não autenticado'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dreams WHERE id = ? AND user_id = ?', (dream_id, user['id']))
    dream = cursor.fetchone()
    conn.close()
    
    if dream:
        return jsonify({
            'ready': True,
            'dream_id': dream_id
        })
    else:
        return jsonify({'ready': False}), 404

@dreams_bp.route('/sonho/<int:dream_id>')
def view_dream(dream_id):
    """Rota para visualizar um sonho específico"""
    user = session.get('user')
    if not user:
        flash('Você precisa estar logado para ver sonhos.', 'error')
        return redirect(url_for('main.index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca o sonho com informações do usuário
    cursor.execute('''
        SELECT d.*, u.username, u.name, u.picture 
        FROM dreams d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    ''', (dream_id,))
    
    dream = cursor.fetchone()
    conn.close()
    
    if not dream:
        flash('Sonho não encontrado.', 'error')
        return redirect(url_for('main.feed'))
    
    # Processa tags
    tags = []
    if dream['tags']:
        try:
            tags = json.loads(dream['tags'])
        except:
            tags = []
    
    return render_template('view_dream.html', user=user, dream=dream, tags=tags)

