"""Rotas para postagem e visualização de sonhos"""
from flask import render_template, session, redirect, url_for, request, flash, jsonify
import logging
import time
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from models import get_db
from config import Config
from . import dreams_bp

logger = logging.getLogger(__name__)

# Configuração de upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# Ajusta o caminho para a pasta static/uploads/dreams relativa ao root do projeto
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'dreams')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Garante que a pasta de upload existe"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        
        # Processa upload de imagem
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ensure_upload_folder()
                # Gera nome único para o arquivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                filename = f"{user['id']}_{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                # Salva caminho relativo
                image_path = f"uploads/dreams/{filename}"
        
        # Salva no banco de dados
        conn = get_db()
        cursor = conn.cursor()
        try:
            tags_json = json.dumps(tags_list) if tags_list else None
            cursor.execute(
                'INSERT INTO dreams (user_id, title, description, dream_type, tags, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                (user['id'], title, description, dream_type, tags_json, image_path)
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

@dreams_bp.route('/sonho/<int:dream_id>/json')
def view_dream_json(dream_id):
    """Rota JSON para obter dados completos do sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.*, u.username, u.name, u.picture 
        FROM dreams d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    ''', (dream_id,))
    
    dream = cursor.fetchone()
    conn.close()
    
    if not dream:
        return jsonify({'success': False, 'error': 'Sonho não encontrado'}), 404
    
    # Processa tags
    tags = []
    if dream['tags']:
        try:
            tags = json.loads(dream['tags'])
        except:
            tags = []
    
    return jsonify({
        'success': True,
        'dream': dict(dream),
        'tags': tags
    })

@dreams_bp.route('/editar-sonho/<int:dream_id>', methods=['GET', 'POST'])
def edit_dream(dream_id):
    """Rota para editar um sonho"""
    user = session.get('user')
    if not user:
        flash('Você precisa estar logado.', 'error')
        return redirect(url_for('main.index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dreams WHERE id = ? AND user_id = ?', (dream_id, user['id']))
    dream = cursor.fetchone()
    
    if not dream:
        conn.close()
        flash('Sonho não encontrado ou você não tem permissão para editá-lo.', 'error')
        return redirect(url_for('main.feed'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        dream_type = request.form.get('dream_type', '').strip()
        tags_input = request.form.get('tags', '').strip()
        
        if not title or not description or not dream_type:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            conn.close()
            return render_template('edit_dream.html', user=user, dream=dream)
        
        # Processa tags
        tags_list = []
        if tags_input:
            tags_clean = tags_input.replace('#', '').replace(',', ' ')
            tags_list = [tag.strip().lower() for tag in tags_clean.split() if tag.strip()]
        
        # Processa upload de nova imagem (se houver)
        image_path = dream['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ensure_upload_folder()
                # Remove imagem antiga se existir
                if image_path:
                    old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', image_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                
                # Salva nova imagem
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                filename = f"{user['id']}_{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = f"uploads/dreams/{filename}"
        
        try:
            tags_json = json.dumps(tags_list) if tags_list else None
            cursor.execute('''
                UPDATE dreams 
                SET title = ?, description = ?, dream_type = ?, tags = ?, image_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (title, description, dream_type, tags_json, image_path, dream_id, user['id']))
            conn.commit()
            conn.close()
            
            flash('Sonho atualizado com sucesso!', 'success')
            return redirect(url_for('dreams.view_dream', dream_id=dream_id))
        except Exception as e:
            conn.close()
            logger.error(f"Erro ao atualizar sonho: {e}")
            flash('Erro ao atualizar o sonho. Tente novamente.', 'error')
            return render_template('edit_dream.html', user=user, dream=dream)
    
    # Processa tags para exibição
    tags = []
    if dream['tags']:
        try:
            tags = json.loads(dream['tags'])
        except:
            tags = []
    
    conn.close()
    return render_template('edit_dream.html', user=user, dream=dream, tags=tags)

@dreams_bp.route('/deletar-sonho/<int:dream_id>', methods=['POST'])
def delete_dream(dream_id):
    """Rota para deletar um sonho"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dreams WHERE id = ? AND user_id = ?', (dream_id, user['id']))
    dream = cursor.fetchone()
    
    if not dream:
        conn.close()
        return jsonify({'success': False, 'error': 'Sonho não encontrado'}), 404
    
    try:
        # Remove imagem se existir
        if dream['image_path']:
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', dream['image_path'])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except:
                    pass
        
        # Deleta sonho (cascata deleta curtidas, favoritos, comentários, histórico)
        cursor.execute('DELETE FROM dreams WHERE id = ? AND user_id = ?', (dream_id, user['id']))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        logger.error(f"Erro ao deletar sonho: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


