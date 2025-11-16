from database_manager import crear_tabla 
from activo_model import Activo
import os

# --- 1. Inicializar la Base de Datos ---
print("--- Inicializando Base de Datos ---")
crear_tabla() # Aseguramos que la tabla exista

# --- 2. Agregar Tipos de Activos Iniciales ---
print("\n--- PASO 2: AGREGANDO ACTIVOS AL INVENTARIO TOTAL ---")
a1 = Activo("MESA-01", "Mesas Plegables Blancas", 30, 30) # Total 30, 30 disponibles
a2 = Activo("CABLE-05", "Cable de Extensión 5m", 50, 50)  # Total 50, 50 disponibles
a3 = Activo("SILLA-02", "Sillas de Conferencia", 100, 100) # Total 100, 100 disponibles

Activo.agregar_tipo_activo(a1)
Activo.agregar_tipo_activo(a2)
Activo.agregar_tipo_activo(a3)

# --- 3. Revisar el Inventario Inicial ---
print("\n--- PASO 3: INVENTARIO INICIAL ---")
inventario = Activo.obtener_todos()
for activo in inventario:
    print(f"[{activo.codigo}] {activo.nombre} | Total: {activo.total_unidades} | Disponibles: {activo.disponibles} | Prestados: {activo.total_unidades - activo.disponibles}")

# --- 4. Registrar Préstamos a Arrendatarios ---
print("\n--- PASO 4: REGISTRANDO PRÉSTAMOS ---")

# La tienda de electrónica pide 15 cables
Activo.prestar_activo("CABLE-05", 15) 

# La cafetería pide 5 mesas
Activo.prestar_activo("MESA-01", 5) 

# Intento fallido: Pedir más sillas de las que hay (si el total fuera 50)
Activo.prestar_activo("SILLA-02", 150) 


# --- 5. Registrar Devoluciones ---
print("\n--- PASO 5: REGISTRANDO DEVOLUCIONES ---")

# La cafetería devuelve 3 mesas
Activo.devolver_activo("MESA-01", 3) 

# Intento fallido: Intentar devolver más cables de los que se prestaron (solo se prestaron 15)
Activo.devolver_activo("CABLE-05", 20) 


# --- 6. Revisar el Inventario Final ---
print("\n--- PASO 6: INVENTARIO FINAL ---")
inventario_final = Activo.obtener_todos()
for activo in inventario_final:
    prestados = activo.total_unidades - activo.disponibles
    print(f"[{activo.codigo}] {activo.nombre} | Disponibles: {activo.disponibles} | Prestados: {prestados}")