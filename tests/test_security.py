"""
Tests para seguridad del sistema
"""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestPasswordSecurity:
    """Tests para seguridad de contraseñas"""
    
    def test_password_hashing(self):
        """Test: Las contraseñas se hashean correctamente"""
        password = 'mi_password_secreto123'
        hashed = generate_password_hash(password)
        
        # El hash no debe ser igual al password original
        assert hashed != password
        
        # Debe poder verificarse correctamente
        assert check_password_hash(hashed, password) is True
        
        # No debe verificarse con contraseña incorrecta
        assert check_password_hash(hashed, 'password_incorrecto') is False
    
    def test_password_hash_uniqueness(self):
        """Test: Cada hash de la misma contraseña es único"""
        password = 'test_password'
        hash1 = generate_password_hash(password)
        hash2 = generate_password_hash(password)
        
        # Los hashes deben ser diferentes (salt único)
        assert hash1 != hash2
        
        # Pero ambos deben verificarse correctamente
        assert check_password_hash(hash1, password) is True
        assert check_password_hash(hash2, password) is True
    
    def test_password_hash_strength(self):
        """Test: Los hashes generados tienen suficiente longitud"""
        password = 'test_password'
        hashed = generate_password_hash(password)
        
        # Hash debe tener longitud mínima
        assert len(hashed) >= 50
        
        # Debe usar un algoritmo seguro (scrypt, bcrypt, pbkdf2, argon2)
        secure_algorithms = ('scrypt:', '$2b$', '$2a$', '$2y$', 'pbkdf2:', '$argon2')
        assert any(hashed.startswith(algo) for algo in secure_algorithms), f"Hash no usa algoritmo seguro: {hashed[:20]}..."

class TestAuthenticationSecurity:
    """Tests para seguridad de autenticación"""
    
    def test_login_required_decorator(self, client, sample_users):
        """Test: Decorador login_required funciona correctamente"""
        # Acceso sin autenticación debe redirigir
        response = client.get('/usuarios')
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Después de login debe permitir acceso
        user = sample_users[0]
        client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        client.post('/login', data={
            'email': user['email'],
            'password': user['password']
        })
        
        response = client.get('/usuarios')
        assert response.status_code == 200
    
    def test_session_isolation(self, client, sample_users):
        """Test: Las sesiones están aisladas correctamente"""
        user1 = sample_users[0]
        user2 = sample_users[1]
        
        # Registrar dos usuarios
        for user in [user1, user2]:
            client.post('/registrar', data={
                'nombre': user['username'],
                'email': user['email'],
                'password': user['password']
            })
        
        # Login con usuario 1
        client.post('/login', data={
            'email': user1['email'],
            'password': user1['password']
        })
        
        # Verificar que solo muestra datos del usuario 1
        response = client.get('/')
        assert user1['username'].encode() in response.data
        
        # Logout y login con usuario 2
        client.get('/logout')
        client.post('/login', data={
            'email': user2['email'],
            'password': user2['password']
        })
        
        # Verificar que ahora muestra datos del usuario 2
        response = client.get('/')
        assert user2['username'].encode() in response.data
    
    def test_logout_clears_session(self, client, authenticated_user):
        """Test: Logout limpia la sesión completamente"""
        # Verificar acceso con sesión
        response = client.get('/usuarios')
        assert response.status_code == 200
        
        # Hacer logout
        client.get('/logout')
        
        # Verificar que ya no puede acceder a página protegida
        response = client.get('/usuarios')
        assert response.status_code == 302
        assert '/login' in response.location

class TestInputSecurity:
    """Tests para seguridad de entrada de datos"""
    
    def test_email_sanitization(self, client):
        """Test: Emails se normalizan correctamente"""
        # Registrar con email en mayúsculas y espacios
        response = client.post('/registrar', data={
            'nombre': 'Test User',
            'email': '  TEST@EXAMPLE.COM  ',
            'password': 'password123'
        })
        
        # Debe registrarse exitosamente
        assert response.status_code == 302
        
        # Login con email normalizado
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Debe poder hacer login
        assert response.status_code == 302
    
    def test_name_sanitization(self, client):
        """Test: Nombres se limpian de espacios extra"""
        response = client.post('/registrar', data={
            'nombre': '  Juan Pérez  ',
            'email': 'juan@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 302
        
        # Login y verificar que el nombre se muestra limpio
        client.post('/login', data={
            'email': 'juan@test.com',
            'password': 'password123'
        })
        
        response = client.get('/')
        # Debe mostrar el nombre sin espacios extra
        assert b'Juan P' in response.data
    
    def test_sql_injection_prevention(self, client):
        """Test: Prevención de inyección SQL"""
        # Intentar inyección SQL en campo email
        malicious_email = "test@test.com'; DROP TABLE users; --"
        
        response = client.post('/login', data={
            'email': malicious_email,
            'password': 'anypassword'
        })
        
        # No debe causar error del servidor
        assert response.status_code == 200
        
        # Intentar registrar usuario normal después (tabla debe existir)
        response = client.post('/registrar', data={
            'nombre': 'Test User',
            'email': 'safe@test.com',
            'password': 'password123'
        })
        
        # Debe funcionar normalmente
        assert response.status_code == 302
    
    def test_xss_prevention(self, client):
        """Test: Prevención de XSS en nombres"""
        malicious_name = "<script>alert('XSS')</script>"
        
        response = client.post('/registrar', data={
            'nombre': malicious_name,
            'email': 'test@test.com',
            'password': 'password123'
        })
        
        if response.status_code == 302:  # Si el registro fue exitoso
            client.post('/login', data={
                'email': 'test@test.com',
                'password': 'password123'
            })
            
            response = client.get('/')
            # El script no debe aparecer ejecutable
            assert b'<script>' not in response.data
            assert b'&lt;script&gt;' in response.data or b'script' not in response.data.lower()

class TestSessionSecurity:
    """Tests para seguridad de sesiones"""
    
    def test_session_timeout_configured(self, client):
        """Test: Timeout de sesión está configurado"""
        from main import app
        # Verificar que hay un timeout configurado
        assert app.permanent_session_lifetime is not None
        assert app.permanent_session_lifetime.total_seconds() > 0
    
    def test_secure_session_key(self):
        """Test: Clave de sesión está configurada"""
        from main import app
        # Verificar que hay secret_key configurada
        assert app.secret_key is not None
        assert len(app.secret_key) > 0
    
    def test_session_data_isolation(self, client, sample_users):
        """Test: Datos de sesión no se mezclan entre usuarios"""
        user1 = sample_users[0]
        
        # Registrar y hacer login
        client.post('/registrar', data={
            'nombre': user1['username'],
            'email': user1['email'],
            'password': user1['password']
        })
        
        client.post('/login', data={
            'email': user1['email'],
            'password': user1['password']
        })
        
        # Obtener página home
        response1 = client.get('/')
        
        # Hacer logout
        client.get('/logout')
        
        # Obtener página home sin sesión
        response2 = client.get('/')
        
        # Las respuestas deben ser diferentes
        assert response1.data != response2.data