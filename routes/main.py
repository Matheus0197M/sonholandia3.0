"""Rotas principais da aplicação"""
from flask import render_template, session, redirect, url_for
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
    return render_template('feed.html', user=user)

