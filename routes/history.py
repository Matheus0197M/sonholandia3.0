"""Rotas para histórico do usuário"""
from flask import render_template, session, redirect, url_for
from models import get_db
from . import main_bp

@main_bp.route('/historico')
def history():
    """Página de histórico do usuário"""
    user = session.get('user')
    if not user:
        return redirect(url_for('main.index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca histórico do usuário
    cursor.execute('''
        SELECT h.*, d.title, d.id as dream_id, d.dream_type,
               u.username, u.name, u.picture
        FROM history h
        JOIN dreams d ON h.dream_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE h.user_id = ?
        ORDER BY h.created_at DESC
        LIMIT 100
    ''', (user['id'],))
    
    history_items = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', user=user, history_items=history_items)



