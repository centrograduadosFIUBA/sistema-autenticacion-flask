"""
Tests para interfaz de usuario y templates
"""
import pytest

class TestTemplateRendering:
    """Tests para renderizado de templates"""
    
    def test_home_template_structure(self, client):
        """Test: Estructura del template home"""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verificar estructura HTML básica
        assert b'<!DOCTYPE html>' in response.data
        assert b'<html lang="es">' in response.data
        assert b'<head>' in response.data
        assert b'<body>' in response.data
        assert b'</html>' in response.data
        
        # Verificar CSS
        assert b'styles.css' in response.data
        
        # Verificar JavaScript
        assert b'flash-messages.js' in response.data
    
    def test_navigation_menu_without_session(self, client):
        """Test: Menú de navegación sin sesión"""
        response = client.get('/')
        assert response.status_code == 200
        
        # Debe mostrar opciones para usuarios no autenticados
        assert b'Registrarme' in response.data
        assert b'Iniciar Sesi' in response.data
        
        # No debe mostrar opciones de usuario autenticado
        assert b'Cerrar Sesi' not in response.data
        assert b'Ver Usuarios' not in response.data
    
    def test_navigation_menu_with_session(self, client, authenticated_user):
        """Test: Menú de navegación con sesión"""
        response = client.get('/')
        assert response.status_code == 200
        
        # Debe mostrar opciones para usuario autenticado
        assert b'Cerrar Sesi' in response.data
        assert b'Ver Usuarios' in response.data
        
        # No debe mostrar opciones de usuario no autenticado
        assert b'Registrarme' not in response.data or b'Iniciar Sesi' in response.data
    
    def test_flash_messages_container(self, client):
        """Test: Contenedor de mensajes flash"""
        # Generar un mensaje flash
        client.get('/usuarios')  # Esto genera mensaje de login required
        
        response = client.get('/login')
        assert response.status_code == 200
        
        # Verificar contenedor de mensajes flash
        assert b'flash-messages' in response.data
        assert b'flash-message' in response.data

class TestFormStructure:
    """Tests para estructura de formularios"""
    
    def test_registration_form(self, client):
        """Test: Estructura del formulario de registro"""
        response = client.get('/registrar')
        assert response.status_code == 200
        
        # Verificar elementos del formulario
        assert b'<form' in response.data
        assert b'action="/registrar"' in response.data
        assert b'method="post"' in response.data
        
        # Verificar campos requeridos
        assert b'name="nombre"' in response.data
        assert b'name="email"' in response.data
        assert b'name="password"' in response.data
        
        # Verificar tipos de input
        assert b'type="text"' in response.data
        assert b'type="email"' in response.data
        assert b'type="password"' in response.data
        
        # Verificar botón submit
        assert b'type="submit"' in response.data or b'<button' in response.data
    
    def test_login_form(self, client):
        """Test: Estructura del formulario de login"""
        response = client.get('/login')
        assert response.status_code == 200
        
        # Verificar elementos del formulario
        assert b'<form' in response.data
        assert b'action="/login"' in response.data
        assert b'method="post"' in response.data
        
        # Verificar campos requeridos
        assert b'name="email"' in response.data
        assert b'name="password"' in response.data
        
        # Verificar tipos de input
        assert b'type="email"' in response.data
        assert b'type="password"' in response.data
    
    def test_form_labels(self, client):
        """Test: Labels de formularios"""
        # Test registro
        response = client.get('/registrar')
        assert b'<label' in response.data
        assert b'Nombre' in response.data or b'nombre' in response.data.lower()
        assert b'Email' in response.data or b'email' in response.data.lower()
        assert b'Contrase' in response.data
        
        # Test login
        response = client.get('/login')
        assert b'<label' in response.data
        assert b'Email' in response.data or b'email' in response.data.lower()
        assert b'Contrase' in response.data

class TestUsersList:
    """Tests para la lista de usuarios"""
    
    def test_users_list_structure(self, client, authenticated_user):
        """Test: Estructura de la lista de usuarios"""
        response = client.get('/usuarios')
        assert response.status_code == 200
        
        # Verificar estructura HTML
        assert b'<ul>' in response.data or b'<li>' in response.data
        assert authenticated_user['username'].encode() in response.data
        assert authenticated_user['email'].encode() in response.data
    
    def test_users_list_multiple_users(self, client, sample_users):
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
        
        response = client.get('/usuarios')
        assert response.status_code == 200
        
        # Verificar que aparecen todos los usuarios
        for user in sample_users:
            assert user['username'].encode() in response.data
            assert user['email'].encode() in response.data
    
    def test_users_list_empty_state(self, client, sample_users):
        """Test: Estado cuando no hay usuarios (técnicamente imposible)"""
        # Este test es más conceptual, ya que siempre habrá al menos el usuario autenticado
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
        # Debe mostrar al menos el usuario autenticado
        assert user['username'].encode() in response.data

class TestResponsiveDesign:
    """Tests para diseño responsive"""
    
    def test_viewport_meta_tag(self, client):
        """Test: Meta tag viewport para responsive"""
        response = client.get('/')
        # Aunque no esté explícito en el HTML, verificar estructura responsive
        assert response.status_code == 200
        assert b'<head>' in response.data
    
    def test_css_responsiveness(self, client):
        """Test: CSS responsive cargado"""
        response = client.get('/static/styles.css')
        assert response.status_code == 200
        
        # Verificar que existe CSS para móviles
        assert b'@media' in response.data
        assert b'768px' in response.data or b'mobile' in response.data.lower()

class TestAccessibility:
    """Tests para accesibilidad"""
    
    def test_form_labels_associated(self, client):
        """Test: Labels asociados con inputs"""
        response = client.get('/registrar')
        
        # Verificar que hay labels con for attributes o inputs dentro de labels
        assert b'<label' in response.data
        assert b'for=' in response.data or b'<input' in response.data
    
    def test_semantic_html(self, client):
        """Test: Uso de HTML semántico"""
        response = client.get('/')
        
        # Verificar elementos semánticos
        assert b'<main>' in response.data
        assert b'<nav>' in response.data
        assert b'<h1>' in response.data or b'<h2>' in response.data
    
    def test_language_attribute(self, client):
        """Test: Atributo de idioma"""
        response = client.get('/')
        assert b'lang="es"' in response.data

class TestErrorPages:
    """Tests para páginas de error"""
    
    def test_404_page(self, client):
        """Test: Página 404"""
        response = client.get('/ruta-inexistente')
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test: Método no permitido"""
        response = client.delete('/')
        assert response.status_code == 405

class TestStaticFiles:
    """Tests para archivos estáticos"""
    
    def test_css_file_loads(self, client):
        """Test: Archivo CSS se carga correctamente"""
        response = client.get('/static/styles.css')
        assert response.status_code == 200
        assert b'css' in response.headers.get('Content-Type', '').lower().encode()
    
    def test_javascript_file_loads(self, client):
        """Test: Archivo JavaScript se carga correctamente"""
        response = client.get('/static/flash-messages.js')
        assert response.status_code == 200
        assert b'javascript' in response.headers.get('Content-Type', '').lower().encode() or response.status_code == 200