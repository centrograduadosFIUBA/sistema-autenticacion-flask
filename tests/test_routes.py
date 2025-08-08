"""
Tests para rutas y endpoints HTTP
"""
import pytest

class TestHomeRoute:
    """Tests para la ruta principal"""
    
    def test_home_without_session(self, client):
        """Test: Página home sin sesión activa"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Bienvenido a mi Aplicaci' in response.data
        assert b'registrarte' in response.data or b'Registrarme' in response.data
    
    def test_home_with_session(self, client, authenticated_user):
        """Test: Página home con sesión activa"""
        response = client.get('/')
        assert response.status_code == 200
        assert authenticated_user['username'].encode() in response.data
        assert b'Cerrar Sesi' in response.data

class TestRegistrationRoute:
    """Tests para la ruta de registro"""
    
    def test_registro_get(self, client):
        """Test: GET a página de registro"""
        response = client.get('/registrar')
        assert response.status_code == 200
        assert b'Crea tu cuenta' in response.data or b'registro' in response.data.lower()
        assert b'<form' in response.data
        assert b'nombre' in response.data.lower()
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()
    
    def test_registro_post_success(self, client, sample_users):
        """Test: POST exitoso a registro"""
        user = sample_users[0]
        response = client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        })
        
        # Debe redirigir a home
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    def test_registro_post_invalid(self, client):
        """Test: POST con datos inválidos"""
        response = client.post('/registrar', data={
            'nombre': '',
            'email': 'invalid',
            'password': '123'
        })
        
        # Debe mostrar formulario nuevamente
        assert response.status_code == 200

class TestLoginRoute:
    """Tests para la ruta de login"""
    
    def test_login_get(self, client):
        """Test: GET a página de login"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Iniciar Sesi' in response.data
        assert b'<form' in response.data
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()
    
    def test_login_post_success(self, client, sample_users):
        """Test: POST exitoso a login"""
        user = sample_users[0]
        
        # Registrar usuario primero
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
        
        # Debe redirigir a home
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    def test_login_post_invalid(self, client):
        """Test: POST con credenciales inválidas"""
        response = client.post('/login', data={
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        })
        
        # Debe mostrar login nuevamente
        assert response.status_code == 200

class TestUsuariosRoute:
    """Tests para la ruta de usuarios (protegida)"""
    
    def test_usuarios_without_auth(self, client):
        """Test: Acceso sin autenticación"""
        response = client.get('/usuarios')
        
        # Debe redirigir a login
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_usuarios_with_auth(self, client, authenticated_user):
        """Test: Acceso con autenticación"""
        response = client.get('/usuarios')
        assert response.status_code == 200
        assert authenticated_user['username'].encode() in response.data
        assert authenticated_user['email'].encode() in response.data
    
    def test_usuarios_multiple_users(self, client, sample_users):
        """Test: Lista con múltiples usuarios"""
        # Registrar múltiples usuarios
        for user in sample_users:
            client.post('/registrar', data={
                'nombre': user['username'],
                'email': user['email'],
                'password': user['password']
            })
        
        # Login con primer usuario
        client.post('/login', data={
            'email': sample_users[0]['email'],
            'password': sample_users[0]['password']
        })
        
        # Verificar lista de usuarios
        response = client.get('/usuarios')
        assert response.status_code == 200
        
        # Verificar que aparecen todos los usuarios
        for user in sample_users:
            assert user['username'].encode() in response.data
            assert user['email'].encode() in response.data

class TestLogoutRoute:
    """Tests para la ruta de logout"""
    
    def test_logout_with_session(self, client, authenticated_user):
        """Test: Logout con sesión activa"""
        response = client.get('/logout')
        
        # Debe redirigir a home
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    def test_logout_without_session(self, client):
        """Test: Logout sin sesión activa"""
        response = client.get('/logout')
        
        # Debe redirigir a home sin error
        assert response.status_code == 302
        assert response.location.endswith('/')

class TestFlashMessages:
    """Tests para mensajes flash en rutas"""
    
    def test_flash_message_login_required(self, client):
        """Test: Mensaje flash cuando se requiere login"""
        # Intentar acceder a página protegida
        client.get('/usuarios')
        
        # Seguir redirección a login
        response = client.get('/login')
        assert response.status_code == 200
        
        # El HTML debe contener el div de flash messages
        assert b'flash-message' in response.data or b'flash' in response.data.lower()
    
    def test_flash_message_successful_registration(self, client, sample_users):
        """Test: Mensaje flash tras registro exitoso"""
        user = sample_users[0]
        
        # Registrar usuario
        response = client.post('/registrar', data={
            'nombre': user['username'],
            'email': user['email'],
            'password': user['password']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Verificar que hay mensaje de éxito
        assert b'flash' in response.data.lower()
    
    def test_flash_message_failed_login(self, client):
        """Test: Mensaje flash tras login fallido"""
        response = client.post('/login', data={
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        # Verificar que hay mensaje de error
        assert b'flash' in response.data.lower()

class TestErrorHandling:
    """Tests para manejo de errores HTTP"""
    
    def test_nonexistent_route(self, client):
        """Test: Ruta que no existe"""
        response = client.get('/ruta-inexistente')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test: Método HTTP no permitido"""
        # Intentar DELETE en ruta que no lo acepta
        response = client.delete('/')
        assert response.status_code == 405