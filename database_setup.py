# database_setup.py
import sqlite3

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de usuarios solo si no existe
# Se usará TEXT para el usuario, email y la contraseña hasheada
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

print("Tabla 'users' creada o ya existente.")

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

# archivo para BD