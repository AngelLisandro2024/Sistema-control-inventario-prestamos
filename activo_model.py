import sqlite3
from database_manager import get_db_connection
from datetime import datetime

class Activo:
    def __init__(self, codigo, nombre, total_unidades, disponibles):
        self.codigo = codigo.upper()
        self.nombre = nombre
        self.total_unidades = total_unidades
        self.disponibles = disponibles

    # --- Lógica CRUD Básica (CREATE, READ, UPDATE) ---

    @staticmethod
    def agregar_tipo_activo(activo):
        """Agrega un nuevo tipo de activo o actualiza las unidades si ya existe."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT total_unidades, disponibles FROM activos WHERE codigo = ?", (activo.codigo,))
        registro = cursor.fetchone()
        
        if registro:
            nueva_total = registro[0] + activo.total_unidades
            nueva_disponible = registro[1] + activo.total_unidades
            
            cursor.execute("""
                UPDATE activos SET nombre = ?, total_unidades = ?, disponibles = ?
                WHERE codigo = ?
            """, (activo.nombre, nueva_total, nueva_disponible, activo.codigo))
        else:
            cursor.execute("""
                INSERT INTO activos (codigo, nombre, total_unidades, disponibles)
                VALUES (?, ?, ?, ?)
            """, (activo.codigo, activo.nombre, activo.total_unidades, activo.disponibles))
            
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def obtener_todos():
        """Devuelve una lista de todos los objetos Activo en el inventario."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, total_unidades, disponibles FROM activos ORDER BY codigo")
        registros = cursor.fetchall()
        conn.close()
        
        activos = []
        for reg in registros:
            activos.append(Activo(reg[0], reg[1], reg[2], reg[3]))
        return activos

    @staticmethod
    def obtener_por_codigo(codigo):
        """Busca un activo por su código."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, total_unidades, disponibles FROM activos WHERE codigo = ?", (codigo.upper(),))
        reg = cursor.fetchone()
        conn.close()
        
        if reg:
            return Activo(reg[0], reg[1], reg[2], reg[3])
        return None

    @staticmethod
    def eliminar_activo(codigo):
        """
        Elimina un tipo de activo. Solo si no hay unidades prestadas.
        """
        activo = Activo.obtener_por_codigo(codigo)
        if not activo:
            return False 
            
        if activo.disponibles != activo.total_unidades:
            return "UNITS_OUT"

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM activos WHERE codigo = ?", (codigo.upper(),))
        cursor.execute("DELETE FROM historial WHERE codigo_activo = ?", (codigo.upper(),))
        
        conn.commit()
        conn.close()
        return True

    # --- Lógica de Préstamos y Devoluciones ---

    @staticmethod
    def prestar_activo(codigo, cantidad, local):
        """Registra un préstamo y actualiza las unidades disponibles."""
        activo = Activo.obtener_por_codigo(codigo)
        
        if not activo or activo.disponibles < cantidad:
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Actualizar unidades disponibles
        nueva_disponible = activo.disponibles - cantidad
        cursor.execute("UPDATE activos SET disponibles = ? WHERE codigo = ?", (nueva_disponible, codigo.upper()))
        
        # 2. Registrar el préstamo en el historial
        fecha_prestamo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO historial (local, codigo_activo, cantidad, fecha_prestamo)
            VALUES (?, ?, ?, ?)
        """, (local, codigo.upper(), cantidad, fecha_prestamo))
        
        conn.commit()
        conn.close()
        return True

    # --- LÓGICA CLAVE: DEVOLUCIÓN (FINAL) ---
    @staticmethod
    def devolver_activo(codigo, cantidad):
        """
        Registra una devolución como un NUEVO registro en el historial para 
        guardar la cantidad devuelta y actualiza el stock.
        """
        activo = Activo.obtener_por_codigo(codigo)
        
        if not activo:
            return False 

        prestadas_actualmente = activo.total_unidades - activo.disponibles
        
        if cantidad > prestadas_actualmente:
            return "TOO_MANY"

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Actualizar unidades disponibles (siempre aumenta)
            nueva_disponible = activo.disponibles + cantidad
            cursor.execute("UPDATE activos SET disponibles = ? WHERE codigo = ?", (nueva_disponible, codigo.upper()))
            
            # 2. Registrar la DEVOLUCIÓN en el historial como un nuevo evento.
            fecha_devolucion_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Construimos el texto del local primero para evitar errores de sintaxis o fallos.
            local_registro = f"DEVOLUCIÓN PARCIAL ({cantidad} uds)" 

            cursor.execute("""
                INSERT INTO historial (local, codigo_activo, cantidad, fecha_devolucion)
                VALUES (?, ?, ?, ?)
            """, (local_registro, codigo.upper(), cantidad, fecha_devolucion_registro))

            conn.commit()
            return True
            
        except sqlite3.Error as e:
            # Captura cualquier error de SQLite que pueda estar causando el bloqueo silencioso
            print(f"Error de SQL al devolver activo: {e}")
            conn.rollback()
            return "DB_ERROR"
        
        finally:
            conn.close()

    @staticmethod
    def obtener_historial_prestamos():
        """Obtiene el historial de préstamos."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ordenamos por fecha de préstamo descendente, luego por fecha de devolución
        cursor.execute("""
            SELECT 
                h.local, 
                a.nombre, 
                h.cantidad, 
                h.fecha_prestamo, 
                h.fecha_devolucion
            FROM historial h
            JOIN activos a ON h.codigo_activo = a.codigo
            ORDER BY h.fecha_prestamo DESC, h.fecha_devolucion DESC
        """)
        historial = cursor.fetchall()
        conn.close()
        return historial