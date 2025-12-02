"""Modelos de banco de dados"""
import sqlite3
import os
from datetime import datetime, timedelta
import secrets

from config import Config

def get_db():
    """Obtém conexão com o banco de dados"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de tokens de reset de senha
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de sonhos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dreams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            dream_type TEXT NOT NULL,
            tags TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de curtidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dream_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, dream_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (dream_id) REFERENCES dreams(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de favoritos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dream_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, dream_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (dream_id) REFERENCES dreams(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dream_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (dream_id) REFERENCES dreams(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de histórico de navegação
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dream_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (dream_id) REFERENCES dreams(id) ON DELETE CASCADE
        )
    ''')
    
    # Índices para melhor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_likes_dream ON likes(dream_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_dream ON comments(dream_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)')
    
    conn.commit()
    conn.close()

def create_password_reset_token(user_id):
    """Cria um token de reset de senha"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Remove tokens antigos não usados
    cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = ? AND (used = 1 OR expires_at < ?)', 
                   (user_id, datetime.now()))
    
    # Gera novo token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
    
    cursor.execute(
        'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
        (user_id, token, expires_at)
    )
    conn.commit()
    conn.close()
    
    return token

def validate_password_reset_token(token):
    """Valida um token de reset de senha"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM password_reset_tokens 
        WHERE token = ? AND used = 0 AND expires_at > ?
    ''', (token, datetime.now()))
    
    token_data = cursor.fetchone()
    conn.close()
    
    return token_data

def mark_token_as_used(token):
    """Marca um token como usado"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
    conn.commit()
    conn.close()

