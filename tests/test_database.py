"""
Tests para operaciones de base de datos
"""
import pytest
import sqlite3
import tempfile
import os
from werkzeug.security import generate_password_hash, check_password_hash
from tests.conftest import temp_database
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import get_db_connection, create_user_in_database, authenticate_user, validate_user_input

class TestDatabaseOperations:
    """Tests para operaciones básicas de base de datos"""
    
    def test_create_user_success(self, sample_users):
        """Test: Crear usuario exitosamente"""
        user = sample_users[0]
        hashed_password = generate_password_hash(user['password'])
        
        with temp_database() as db_path:
            # Usar la función del sistema
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                create_user_in_database(user['username'], user['email'], hashed_password)
                
                # Verificar que el usuario fue creado
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (user['email'].lower(),))
                result = cursor.fetchone()
                conn.close()
                
                assert result is not None
                assert result[1] == user['username']
                assert result[2] == user['email'].lower()
                assert check_password_hash(result[3], user['password'])
            
            finally:
                __import__('main').DATABASE_PATH = original_path
    
    def test_create_user_duplicate_email(self, sample_users):
        """Test: Error al crear usuario con email duplicado"""
        user = sample_users[0]
        hashed_password = generate_password_hash(user['password'])
        
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                # Crear primer usuario
                create_user_in_database(user['username'], user['email'], hashed_password)
                
                # Intentar crear segundo usuario con mismo email
                with pytest.raises(Exception):
                    create_user_in_database('Otro Usuario', user['email'], hashed_password)
            
            finally:
                __import__('main').DATABASE_PATH = original_path
    
    def test_authenticate_user_success(self, sample_users):
        """Test: Autenticación exitosa"""
        user = sample_users[0]
        hashed_password = generate_password_hash(user['password'])
        
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                # Crear usuario
                create_user_in_database(user['username'], user['email'], hashed_password)
                
                # Autenticar
                result = authenticate_user(user['email'], user['password'])
                
                assert result is not None
                assert result['username'] == user['username']
                assert result['email'] == user['email'].lower()
            
            finally:
                __import__('main').DATABASE_PATH = original_path
    
    def test_authenticate_user_wrong_password(self, sample_users):
        """Test: Autenticación fallida con contraseña incorrecta"""
        user = sample_users[0]
        hashed_password = generate_password_hash(user['password'])
        
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                # Crear usuario
                create_user_in_database(user['username'], user['email'], hashed_password)
                
                # Intentar autenticar con contraseña incorrecta
                result = authenticate_user(user['email'], 'wrong_password')
                
                assert result is None
            
            finally:
                __import__('main').DATABASE_PATH = original_path
    
    def test_authenticate_user_nonexistent(self):
        """Test: Autenticación fallida con usuario inexistente"""
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                result = authenticate_user('inexistente@test.com', 'anypassword')
                assert result is None
            
            finally:
                __import__('main').DATABASE_PATH = original_path

class TestDatabaseConnection:
    """Tests para manejo de conexiones de base de datos"""
    
    def test_connection_context_manager(self):
        """Test: Context manager para conexiones"""
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                # Test conexión exitosa
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT 1')
                    result = cursor.fetchone()
                    assert result[0] == 1
            
            finally:
                __import__('main').DATABASE_PATH = original_path
    
    def test_database_rollback_on_error(self):
        """Test: Rollback automático en caso de error"""
        with temp_database() as db_path:
            original_path = __import__('main').DATABASE_PATH
            __import__('main').DATABASE_PATH = db_path
            
            try:
                # Intentar operación que genere error
                with pytest.raises(Exception):
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        # Query inválida
                        cursor.execute('INVALID SQL QUERY')
            
            finally:
                __import__('main').DATABASE_PATH = original_path

class TestDataValidation:
    """Tests para validación de datos"""
    
    def test_validate_user_input_success(self):
        """Test: Validación exitosa de datos"""
        errors = validate_user_input('Juan Pérez', 'juan@test.com', 'password123')
        assert len(errors) == 0
    
    def test_validate_user_input_short_name(self):
        """Test: Error con nombre muy corto"""
        errors = validate_user_input('A', 'juan@test.com', 'password123')
        assert len(errors) > 0
        assert any('nombre' in error.lower() for error in errors)
    
    def test_validate_user_input_invalid_email(self):
        """Test: Error con email inválido"""
        errors = validate_user_input('Juan Pérez', 'invalid-email', 'password123')
        assert len(errors) > 0
        assert any('email' in error.lower() for error in errors)
    
    def test_validate_user_input_short_password(self):
        """Test: Error con contraseña muy corta"""
        errors = validate_user_input('Juan Pérez', 'juan@test.com', '123')
        assert len(errors) > 0
        assert any('contraseña' in error.lower() for error in errors)
    
    def test_validate_user_input_multiple_errors(self):
        """Test: Múltiples errores de validación"""
        errors = validate_user_input('A', 'invalid', '12')
        assert len(errors) >= 3  # Nombre, email y contraseña inválidos