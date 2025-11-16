import sqlite3
import os

DB_NAME = 'inventario.db'

def get_db_connection():
    """
    Crea y devuelve una nueva conexión a la base de datos 'inventario.db'.
    Cada vez que se llama, abre una nueva conexión, la cual DEBE cerrarse
    explícitamente en el archivo 'activo_model.py'.
    """
    # Intentamos conectar a la base de datos
    try:
        # Crea el archivo si no existe y abre la conexión
        conn = sqlite3.connect(DB_NAME) 
        return conn
    except sqlite3.Error as e:
        # En caso de error de conexión, imprime el error y devuelve None
        print(f"Error al conectar a la base de datos: {e}")
        return None

def crear_tabla():
    """Crea las tablas 'activos' e 'historial' si no existen."""
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    
    # Tabla de Activos (Stock Actual)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            total_unidades INTEGER NOT NULL,
            disponibles INTEGER NOT NULL
        )
    """)
    
    # Tabla de Historial (Préstamos y Devoluciones)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            local TEXT NOT NULL,
            codigo_activo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha_prestamo TEXT,
            fecha_devolucion TEXT,
            FOREIGN KEY (codigo_activo) REFERENCES activos (codigo)
        )
    """)
    
    conn.commit()
    conn.close()