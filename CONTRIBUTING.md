# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Autenticación Flask! Esta guía te ayudará a comenzar.

## 🚀 Inicio Rápido

### Configurar el Entorno de Desarrollo

```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tuusuario/sistema-autenticacion-flask.git
cd sistema-autenticacion-flask

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -e .

# 4. Configurar base de datos
python database_setup.py

# 5. Ejecutar tests para verificar
python run_tests.py
```

## 📝 Proceso de Contribución

### 1. Reportar Issues
- Busca issues existentes antes de crear uno nuevo
- Usa templates de issue cuando estén disponibles
- Incluye información detallada:
  - Versión de Python y Flask
  - Sistema operativo
  - Pasos para reproducir
  - Logs relevantes

### 2. Crear Pull Request
1. **Fork** el repositorio
2. **Crear branch**: `git checkout -b feature/mi-nueva-funcionalidad`
3. **Escribir código** siguiendo las convenciones
4. **Añadir tests** para tu funcionalidad
5. **Ejecutar tests**: `python run_tests.py`
6. **Commit**: `git commit -am 'Add: nueva funcionalidad'`
7. **Push**: `git push origin feature/mi-nueva-funcionalidad`
8. **Crear PR** con descripción detallada

## 📏 Estándares de Código

### Python Style Guide
- **PEP 8**: Estilo oficial de Python
- **Line length**: Máximo 88 caracteres (compatible con Black)
- **Imports**: Organizados según PEP 8
- **Docstrings**: Google style para documentación

### Ejemplo de Función Bien Documentada
```python
def create_user_in_database(nombre: str, email: str, hashed_password: str) -> bool:
    """Crea un nuevo usuario en la base de datos.
    
    Args:
        nombre: Nombre completo del usuario
        email: Dirección de correo electrónico válida
        hashed_password: Contraseña ya hasheada usando Werkzeug
    
    Returns:
        True si el usuario fue creado exitosamente, False en caso contrario
    
    Raises:
        DatabaseError: Si hay problemas de conectividad con la base de datos
        ValidationError: Si los datos de entrada no son válidos
    """
    # Implementación aquí
    pass
```

### Convenciones de Naming
```python
# Variables y funciones: snake_case
user_name = "ejemplo"
def get_user_by_email():
    pass

# Clases: PascalCase
class UserManager:
    pass

# Constantes: UPPER_CASE
DATABASE_PATH = "database.db"
MAX_LOGIN_ATTEMPTS = 5
```

## 🧪 Testing Guidelines

### Escribir Tests
```python
import pytest
from main import app, get_db_connection

class TestNewFeature:
    """Tests para la nueva funcionalidad."""
    
    def test_feature_success(self, client):
        """Test de caso exitoso."""
        response = client.post('/nueva-ruta', data={
            'param': 'valor'
        })
        assert response.status_code == 200
        assert 'éxito' in response.get_data(as_text=True)
    
    def test_feature_validation_error(self, client):
        """Test de validación de errores."""
        response = client.post('/nueva-ruta', data={
            'param': ''  # Dato inválido
        })
        assert response.status_code == 400
```

### Categorías de Tests
- **test_auth.py**: Autenticación y sesiones
- **test_database.py**: Operaciones de base de datos
- **test_routes.py**: Endpoints HTTP
- **test_security.py**: Validaciones de seguridad
- **test_ui.py**: Templates e interfaz de usuario

### Ejecutar Tests
```bash
# Suite completa
python run_tests.py

# Tests específicos
python -m pytest tests/test_auth.py -v

# Con cobertura
python -m pytest tests/ --cov=main --cov-report=html

# Tests fallidos solamente
python -m pytest --lf -x
```

## 🛡️ Consideraciones de Seguridad

### Checklist de Seguridad
- [ ] Validación de entrada en todos los endpoints
- [ ] Sanitización de datos antes de almacenar
- [ ] Uso correcto de funciones de hash
- [ ] Prevención de SQL injection
- [ ] Escape de HTML para prevenir XSS
- [ ] Logging de eventos de seguridad
- [ ] Tests de seguridad incluidos

### Ejemplo de Validación Segura
```python
def validate_and_sanitize_input(data: dict) -> dict:
    """Valida y sanitiza datos de entrada."""
    errors = []
    clean_data = {}
    
    # Validar nombre
    if 'nombre' in data:
        nombre = data['nombre'].strip()
        if len(nombre) < 2:
            errors.append("Nombre debe tener al menos 2 caracteres")
        clean_data['nombre'] = nombre
    
    # Validar email
    if 'email' in data:
        email = data['email'].strip().lower()
        if '@' not in email or len(email) < 5:
            errors.append("Email inválido")
        clean_data['email'] = email
    
    if errors:
        raise ValidationError(errors)
    
    return clean_data
```

## 📚 Documentación

### Actualizar Documentación
- Mantener **README.md** actualizado con nuevas features
- Documentar cambios en **replit.md**
- Añadir ejemplos de uso cuando sea relevante
- Actualizar docstrings de funciones modificadas

### Escribir Documentación Clara
```markdown
## Nueva Funcionalidad

### Descripción
Explicación breve de qué hace la funcionalidad.

### Uso
```python
# Ejemplo de código
result = nueva_funcion(parametro="valor")
print(result)
```

### Parámetros
- `parametro` (str): Descripción del parámetro

### Retorna
- dict: Descripción de lo que retorna
```

## 🐛 Debugging Tips

### Logging Efectivo
```python
import logging

# Al inicio del archivo
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# En funciones críticas
def critical_function():
    logger.debug("Iniciando función crítica")
    try:
        # Lógica aquí
        result = some_operation()
        logger.info(f"Operación exitosa: {result}")
        return result
    except Exception as e:
        logger.error(f"Error en función crítica: {e}")
        raise
```

### Usar Breakpoints
```python
# Para debugging interactivo
import pdb; pdb.set_trace()

# O en Python 3.7+
breakpoint()
```

## 🎯 Tipos de Contribuciones Bienvenidas

### 🐛 Bug Fixes
- Corrección de errores existentes
- Mejoras de estabilidad
- Optimizaciones de rendimiento

### ✨ Nuevas Features
- Funcionalidades de autenticación avanzadas
- Mejoras de UI/UX
- Integraciones con servicios externos
- Herramientas de desarrollo

### 📝 Documentación
- Corrección de typos
- Mejora de ejemplos
- Traducción a otros idiomas
- Tutoriales y guías

### 🧪 Testing
- Nuevos tests para casos edge
- Mejora de cobertura de código
- Tests de rendimiento
- Tests de seguridad

## 🏆 Reconocimiento

Los contribuidores serán reconocidos en:
- **README.md** en la sección de agradecimientos
- **CONTRIBUTORS.md** con lista completa
- **Release notes** para contribuciones mayores

## 📞 Obtener Ayuda

¿Tienes preguntas? Puedes:
- Abrir un **Discussion** en GitHub
- Crear un **Issue** con la etiqueta "question"
- Contactar a los mantenedores del proyecto

## 📋 Checklist Pre-Commit

Antes de enviar tu PR, verifica:
- [ ] Tests pasan: `python run_tests.py`
- [ ] Cobertura >85%: `python -m pytest --cov=main`
- [ ] Código formateado: `black main.py tests/`
- [ ] Linting sin errores: `flake8 main.py tests/`
- [ ] Documentación actualizada
- [ ] Commit messages descriptivos
- [ ] Branch actualizado con main

¡Gracias por contribuir al proyecto! 🙌