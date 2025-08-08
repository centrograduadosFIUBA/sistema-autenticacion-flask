"""
Configuración de pytest y fixtures para el sistema de testing
"""
import pytest
import tempfile
import os
import sqlite3
from contextlib import contextmanager
import sys

# Agregar el directorio raíz al path para importar main
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, DATABASE_PATH, get_db_connection

@pytest.fixture
def client():
    """Cliente Flask para testing"""
    # Crear base de datos temporal para tests
    db_fd, temp_db_path = tempfile.mkstemp()
    
    # Configurar app para testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Usar base de datos temporal
    original_db_path = DATABASE_PATH
    import main
    main.DATABASE_PATH = temp_db_path
    
    with app.test_client() as client:
        with app.app_context():
            # Crear tabla de usuarios para tests
            init_test_database(temp_db_path)
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(temp_db_path)
    main.DATABASE_PATH = original_db_path

def init_test_database(db_path):
    """Inicializar base de datos de prueba"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@pytest.fixture
def sample_users():
    """Usuarios de muestra para testing"""
    return [
        {
            'username': 'Juan Pérez',
            'email': 'juan@test.com',
            'password': 'password123'
        },
        {
            'username': 'María García',
            'email': 'maria@test.com',
            'password': 'securepass456'
        },
        {
            'username': 'Carlos López',
            'email': 'carlos@test.com',
            'password': 'mypassword789'
        }
    ]

@pytest.fixture
def authenticated_user(client, sample_users):
    """Usuario autenticado para tests que requieren login"""
    user = sample_users[0]
    
    # Registrar usuario
    client.post('/registrar', data={
        'nombre': user['username'],
        'email': user['email'],
        'password': user['password']
    })
    
    # Login
    response = client.post('/login', data={
        'email': user['email'],
        'password': user['password']
    })
    
    return user

@contextmanager
def temp_database():
    """Context manager para base de datos temporal"""
    db_fd, temp_path = tempfile.mkstemp()
    try:
        init_test_database(temp_path)
        yield temp_path
    finally:
        os.close(db_fd)
        os.unlink(temp_path)