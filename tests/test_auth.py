"""
Tests para el sistema de autenticación
"""
import pytest
from flask import session

class TestRegistration:
    """Tests para el registro de usuarios"""
    
    def test_registro_exitoso(self, client, sample_users):
        """Test: Registro exitoso con datos válidos"""
        user = sample_users[0]
        response = client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        # Verificar redirección a home
        assert response.status_code == 302
        assert response.location.endswith('/')
        
        # Verificar que el usuario puede hacer login
        login_response = client.post('/login', data={
            'email': user['email'],
            'password': user['password']
        })
        assert login_response.status_code == 302
    
    def test_registro_email_duplicado(self, client, sample_users):
        """Test: Registro fallido con email ya existente"""
        user = sample_users[0]
        
        # Primer registro - exitoso
        client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        # Segundo registro con mismo email - debe fallar
        response = client.post('/registrar', data={
            'nombre': 'Otro Usuario',
            'email': user['email'],  # Email duplicado
            'password': 'otrapassword'
        })
        
        # Debe regresar al formulario de registro
        assert response.status_code == 200
        assert b'registro.html' in response.data or b'Crea tu cuenta' in response.data
    
    def test_registro_datos_invalidos(self, client):
        """Test: Registro fallido con datos inválidos"""
        # Nombre muy corto
        response = client.post('/registrar', data={
            'nombre': 'A',  # Muy corto
            'email': 'valid@email.com',
            'password': 'validpassword'
        })
        assert response.status_code == 200
        
        # Email inválido
        response = client.post('/registrar', data={
            'nombre': 'Nombre Válido',
            'email': 'invalid-email',  # Sin @
            'password': 'validpassword'
        })
        assert response.status_code == 200
        
        # Contraseña muy corta
        response = client.post('/registrar', data={
            'nombre': 'Nombre Válido',
            'email': 'valid@email.com',
            'password': '123'  # Muy corta
        })
        assert response.status_code == 200

class TestLogin:
    """Tests para el inicio de sesión"""
    
    def test_login_exitoso(self, client, sample_users):
        """Test: Login exitoso con credenciales correctas"""
        user = sample_users[0]
        
        # Registrar usuario primero
        client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        # Intentar login
        response = client.post('/login', data={
            'email': user['email'],
            'password': user['password']
        })
        
        # Verificar redirección a home
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    def test_login_credenciales_incorrectas(self, client, sample_users):
        """Test: Login fallido con credenciales incorrectas"""
        user = sample_users[0]
        
        # Registrar usuario
        client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        # Login con contraseña incorrecta
        response = client.post('/login', data={
            'email': user['email'],
            'password': 'wrongpassword'
        })
        
        # Debe permanecer en login
        assert response.status_code == 200
        assert b'login.html' in response.data or b'Iniciar' in response.data
    
    def test_login_usuario_inexistente(self, client):
        """Test: Login fallido con usuario que no existe"""
        response = client.post('/login', data={
            'email': 'inexistente@test.com',
            'password': 'anypassword'
        })
        
        # Debe permanecer en login
        assert response.status_code == 200
        assert b'login.html' in response.data or b'Iniciar' in response.data
    
    def test_login_datos_vacios(self, client):
        """Test: Login fallido con datos vacíos"""
        response = client.post('/login', data={
            'email': '',
            'password': ''
        })
        
        # Debe permanecer en login
        assert response.status_code == 200

class TestLogout:
    """Tests para el cierre de sesión"""
    
    def test_logout_exitoso(self, client, authenticated_user):
        """Test: Logout exitoso"""
        # Verificar que hay sesión activa accediendo a página protegida
        usuarios_response = client.get('/usuarios')
        assert usuarios_response.status_code == 200
        
        # Hacer logout
        response = client.get('/logout')
        
        # Verificar redirección a home
        assert response.status_code == 302
        assert response.location.endswith('/')
        
        # Verificar que ya no puede acceder a páginas protegidas
        usuarios_response = client.get('/usuarios')
        assert usuarios_response.status_code == 302  # Redirección a login
    
    def test_logout_sin_sesion(self, client):
        """Test: Logout sin sesión activa"""
        response = client.get('/logout')
        
        # Debe redirigir a home sin error
        assert response.status_code == 302
        assert response.location.endswith('/')

class TestSessionManagement:
    """Tests para manejo de sesiones"""
    
    def test_persistencia_sesion(self, client, authenticated_user):
        """Test: La sesión se mantiene entre requests"""
        # Primera request a página protegida
        response1 = client.get('/usuarios')
        assert response1.status_code == 200
        
        # Segunda request - sesión debe persistir
        response2 = client.get('/usuarios')
        assert response2.status_code == 200
    
    def test_acceso_sin_sesion(self, client):
        """Test: Acceso a página protegida sin sesión"""
        response = client.get('/usuarios')
        
        # Debe redirigir a login
        assert response.status_code == 302
        # La URL debe contener /login
        assert '/login' in response.location