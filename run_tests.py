#!/usr/bin/env python3
"""
Script principal para ejecutar todos los tests del sistema de autenticación Flask
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(text):
    """Imprimir encabezado con formato"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_section(text):
    """Imprimir sección con formato"""
    print(f"\n--- {text} ---")

def run_command(command, description):
    """Ejecutar comando y capturar salida"""
    print(f"Ejecutando: {description}")
    print(f"Comando: {command}")
    
    start_time = time.time()
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"✅ {description} completado en {duration:.2f}s")
        return True, result.stdout, result.stderr
    else:
        print(f"❌ {description} falló en {duration:.2f}s")
        print(f"Error: {result.stderr}")
        return False, result.stdout, result.stderr

def main():
    """Función principal"""
    print_header(f"EJECUCIÓN DE TESTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("❌ Error: No se encuentra main.py. Ejecuta este script desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    # Verificar que existen los archivos de test
    if not os.path.exists('tests'):
        print("❌ Error: No se encuentra el directorio 'tests'. Asegúrate de que los tests estén creados.")
        sys.exit(1)
    
    # Estadísticas
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    test_results = []
    
    print_section("Configuración del entorno")
    
    # Verificar pytest instalado
    success, stdout, stderr = run_command("python -m pytest --version", "Verificación de pytest")
    if not success:
        print("❌ pytest no está instalado o no funciona correctamente")
        print("Instálalo con: pip install pytest pytest-flask pytest-cov")
        sys.exit(1)
    
    print_section("Ejecución de Tests por Categorías")
    
    # Lista de archivos de test
    test_files = [
        ('tests/test_auth.py', 'Tests de Autenticación'),
        ('tests/test_database.py', 'Tests de Base de Datos'),
        ('tests/test_routes.py', 'Tests de Rutas HTTP'),
        ('tests/test_security.py', 'Tests de Seguridad'),
        ('tests/test_ui.py', 'Tests de Interfaz de Usuario')
    ]
    
    # Ejecutar cada categoría de tests
    for test_file, description in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 {description}")
            success, stdout, stderr = run_command(
                f"python -m pytest {test_file} -v --tb=short",
                description
            )
            
            # Parsear resultados
            if "failed" in stdout.lower() or "error" in stdout.lower():
                failed_count = stdout.count("FAILED")
                passed_count = stdout.count("PASSED")
            else:
                failed_count = 0
                passed_count = stdout.count("PASSED") if "PASSED" in stdout else 0
            
            total_tests += passed_count + failed_count
            passed_tests += passed_count
            failed_tests += failed_count
            
            test_results.append({
                'category': description,
                'success': success,
                'passed': passed_count,
                'failed': failed_count,
                'output': stdout[:500] + "..." if len(stdout) > 500 else stdout
            })
        else:
            print(f"⚠️  {test_file} no existe, saltando...")
    
    print_section("Ejecución Completa con Cobertura")
    
    # Ejecutar todos los tests con cobertura
    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --cov=main --cov-report=html --cov-report=term",
        "Tests completos con reporte de cobertura"
    )
    
    # Generar reporte final
    print_header("REPORTE FINAL DE RESULTADOS")
    
    print(f"📊 Estadísticas Generales:")
    print(f"   Total de tests ejecutados: {total_tests}")
    print(f"   Tests pasados: {passed_tests} ✅")
    print(f"   Tests fallidos: {failed_tests} ❌")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("   🎉 ¡Excelente cobertura de tests!")
        elif success_rate >= 75:
            print("   👍 Buena cobertura de tests")
        elif success_rate >= 50:
            print("   ⚠️  Cobertura de tests mejorable")
        else:
            print("   🚨 Cobertura de tests insuficiente")
    
    print(f"\n📋 Resultados por Categoría:")
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {result['category']}: {result['passed']} pasados, {result['failed']} fallidos")
    
    # Información sobre reportes generados
    print(f"\n📄 Reportes Generados:")
    if os.path.exists('htmlcov/index.html'):
        print(f"   📊 Reporte de cobertura HTML: htmlcov/index.html")
    
    print(f"\n⏰ Tests completados: {datetime.now().strftime('%H:%M:%S')}")
    
    # Mostrar archivos de logs si existen
    print_section("Información Adicional")
    print("💡 Para ejecutar tests específicos:")
    print("   python -m pytest tests/test_auth.py -v")
    print("   python -m pytest tests/test_database.py::TestDatabaseOperations -v")
    print("   python -m pytest -k 'test_login' -v")
    
    print("\n💡 Para ver cobertura detallada:")
    print("   python -m pytest --cov=main --cov-report=term-missing")
    
    # Código de salida
    if failed_tests == 0:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed_tests} tests fallaron. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()