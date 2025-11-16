import tkinter as tk
from tkinter import ttk, messagebox
from activo_model import Activo 
from database_manager import crear_tabla 
from reporte_csv import generar_reporte_inventario_csv
import sqlite3

# --- 1. CONFIGURACIÓN INICIAL Y ESTILOS ---
crear_tabla() 

def configurar_estilos():
    """Aplica estilos modernos a la interfaz Tkinter estándar (ttk)."""
    style = ttk.Style()
    style.theme_use('clam') 
    
    COLOR_PRIMARIO = '#3498DB'
    COLOR_TITULO = '#2C3E50'
    COLOR_FONDO = '#ECF0F1'
    
    style.configure('TFrame', background=COLOR_FONDO)
    style.configure('.', background=COLOR_FONDO)
    
    style.configure('TNotebook.Tab', 
                    font=('Arial', 10, 'bold'), 
                    padding=[10, 5],
                    background=COLOR_FONDO,
                    foreground=COLOR_TITULO)
    style.map('TNotebook.Tab', 
              background=[('selected', COLOR_PRIMARIO)],
              foreground=[('selected', 'white')])

    style.configure('TButton', 
                    font=('Arial', 10, 'bold'), 
                    padding=6, 
                    relief='flat', 
                    background='#BDC3C7')
    
    style.configure('Accent.TButton', 
                    background=COLOR_PRIMARIO, 
                    foreground='white')
    style.map('Accent.TButton', 
              background=[('active', '#2980B9')], 
              foreground=[('active', 'white')])

    style.configure("Treeview.Heading", 
                    font=('Arial', 10, 'bold'), 
                    background=COLOR_TITULO, 
                    foreground='white')
    style.configure("Treeview", 
                    rowheight=25, 
                    fieldbackground=COLOR_FONDO)


# --- 2. FUNCIONES DE LÓGICA DE INTERFAZ ---

def cargar_inventario(tree):
    """Limpia y rellena la tabla de INVENTARIO (Treeview)."""
    for item in tree.get_children():
        tree.delete(item)
    activos = Activo.obtener_todos()
    for activo in activos:
        prestados = activo.total_unidades - activo.disponibles
        tree.insert('', tk.END, values=(
            activo.codigo, 
            activo.nombre, 
            activo.total_unidades, 
            activo.disponibles, 
            prestados
        ))
        
def cargar_historial(tree):
    """Limpia y rellena la tabla de HISTORIAL (Treeview)."""
    for item in tree.get_children():
        tree.delete(item)
    historial = Activo.obtener_historial_prestamos()
    
    for registro in historial:
        local, activo, cantidad, f_prestamo, f_devolucion = registro
        
        # --- LÓGICA CLAVE: Identificar el tipo de registro ---
        if f_prestamo and not f_devolucion:
            # Préstamo ABIERTO (Original)
            estado = "PRESTADO"
            color_tag = 'prestado'
            fecha_visible = f_prestamo
            local_fmt = local
        elif not f_prestamo and f_devolucion:
            # Devolución Parcial (Nuevo Registro Creado)
            estado = "DEVUELTO (Parcial)"
            color_tag = 'devuelto'
            fecha_visible = f_devolucion
            # Formato limpio para la columna local
            local_fmt = f"DEVOLUCIÓN DE {cantidad} uds" 
        else:
            # Fallback (Registros antiguos o inconsistentes)
            estado = "ERROR/CERRADO"
            color_tag = 'cerrado'
            fecha_visible = f_prestamo if f_prestamo else f_devolucion
            local_fmt = local
        
        f_visible_fmt = fecha_visible.split(' ')[0] if fecha_visible else ""
        
        # Insertamos los datos en la tabla
        tree.insert('', tk.END, values=(
            local_fmt, 
            activo, 
            cantidad, 
            f_visible_fmt, 
            estado
        ), tags=(color_tag,))
        
    tree.tag_configure('prestado', foreground='#C0392B') # Rojo oscuro
    tree.tag_configure('devuelto', foreground='#27AE60') # Verde oscuro

def eliminar_activo_seleccionado(tree, root, hist_tree):
    """Obtiene el activo seleccionado en la tabla y lo elimina de la BD."""
    
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showerror("Error", "Seleccione un activo de la tabla para eliminar.")
        return

    item = seleccion[0]
    codigo_activo = tree.item(item, 'values')[0]
    nombre_activo = tree.item(item, 'values')[1]

    if messagebox.askyesno("Confirmar Eliminación", 
                           f"¿Está seguro de que desea eliminar el activo:\n\n{codigo_activo} - {nombre_activo}?\n\n¡Esta acción es permanente y eliminará el registro de la base de datos!"):
        
        resultado = Activo.eliminar_activo(codigo_activo)
        
        if resultado is True:
            messagebox.showinfo("Éxito", f"El activo '{codigo_activo}' ha sido eliminado exitosamente.")
            cargar_inventario(tree)
            cargar_historial(hist_tree)
        elif resultado == "UNITS_OUT":
            messagebox.showerror("Error de Eliminación", 
                                 "No se puede eliminar el activo. Debe devolver todas las unidades prestadas primero (Disponibles ≠ Total).")
        else:
            messagebox.showerror("Error", "No se pudo eliminar el activo.")


# --- 3. FORMULARIOS MODALES Y LÓGICA DE ACCIÓN (Corregida) ---

def mostrar_formulario_activo(root, tipo, inv_tree, hist_tree=None):
    """Crea una ventana modal para registrar nuevos activos, préstamos o devoluciones."""
    
    titulo = "NUEVO ACTIVO"
    if tipo == 'prestar': titulo = "REGISTRO DE PRÉSTAMO"
    elif tipo == 'devolver': titulo = "REGISTRO DE DEVOLUCIÓN"
        
    form = tk.Toplevel(root)
    form.title(titulo)
    form.geometry("350x380" if tipo in ['agregar', 'prestar'] else "300x250")
    form.resizable(False, False)
    form.grab_set() 
    
    frame = ttk.Frame(form, padding="15")
    frame.pack(fill='both', expand=True)

    ttk.Label(frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=(5, 15))
    
    # Campo Local (solo para Préstamo)
    if tipo == 'prestar':
        ttk.Label(frame, text="Nombre del Local Arrendatario:").pack(anchor='w')
        local_entry = ttk.Entry(frame, width=40)
        local_entry.pack(pady=3)
    
    # Campo Nombre (solo para Agregar)
    if tipo == 'agregar':
        ttk.Label(frame, text="Nombre/Descripción:").pack(anchor='w')
        nombre_entry = ttk.Entry(frame, width=40)
        nombre_entry.pack(pady=3)
        
    # Campo Código
    ttk.Label(frame, text="Código de Activo:").pack(anchor='w')
    codigo_entry = ttk.Entry(frame, width=40)
    codigo_entry.pack(pady=3)
    
    # Campo Cantidad
    ttk.Label(frame, text=f"Cantidad a {'Dar de Alta' if tipo == 'agregar' else tipo.title()}:").pack(anchor='w')
    cantidad_entry = ttk.Entry(frame, width=40)
    cantidad_entry.pack(pady=3)
    
    # --- Función de Acción (Interna) ---
    def ejecutar_accion():
        codigo = codigo_entry.get().upper().strip()
        
        # Validación de Cantidad (Lectura Robusta)
        cantidad_str = cantidad_entry.get().strip()
        if not cantidad_str:
            messagebox.showerror("Error", "Debe ingresar una cantidad.")
            return

        try:
            cantidad = int(cantidad_str)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero válido.")
            return

        if not codigo or cantidad <= 0:
            messagebox.showerror("Error", "Debe completar el código y la cantidad correctamente.")
            return

        resultado = False
        mensaje_error = "Error de operación."
        
        # Lógica de Acciones
        if tipo == 'agregar':
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Debe ingresar un nombre.")
                return
            nuevo_activo = Activo(codigo, nombre, cantidad, cantidad)
            resultado = Activo.agregar_tipo_activo(nuevo_activo)
            mensaje_error = f"El código '{codigo}' ya existe o la cantidad es inválida."
        
        elif tipo == 'prestar':
            # Verificación del campo local
            local = local_entry.get().strip()
            if not local:
                messagebox.showerror("Error", "Debe ingresar el nombre del local.")
                return
            resultado = Activo.prestar_activo(codigo, cantidad, local)
            mensaje_error = "Stock insuficiente o código no encontrado."
            
        elif tipo == 'devolver':
            # Lógica de Devolución
            resultado = Activo.devolver_activo(codigo, cantidad)
            
            if resultado == "TOO_MANY":
                 mensaje_error = "Error: La cantidad a devolver es mayor a la cantidad actualmente prestada."
                 resultado = False
            elif resultado == "DB_ERROR": # <-- MANEJO DEL NUEVO ERROR DE BASE DE DATOS
                 mensaje_error = "Error crítico al guardar en la base de datos (SQLite). Intente de nuevo."
                 resultado = False
            elif resultado is False:
                 mensaje_error = "Código de activo no encontrado."

        # Mensaje Final y Recarga
        if resultado is True:
            messagebox.showinfo("Éxito", f"Operación de {tipo} realizada con éxito.")
            cargar_inventario(inv_tree)
            
            if hist_tree and (tipo == 'prestar' or tipo == 'devolver'):
                cargar_historial(hist_tree) 

            form.destroy()
        else:
            messagebox.showerror("Error de Operación", mensaje_error)

    # --- Botón de Ejecución (Conexión) ---
    ttk.Button(frame, text=f"CONFIRMAR {tipo.upper()}", command=ejecutar_accion, style='Accent.TButton').pack(pady=15, fill='x')


# --- 4. FUNCIÓN PRINCIPAL DE LA VENTANA (ROOT) ---

def main_window():
    root = tk.Tk()
    root.title("Inventario | Control de Activos")
    root.geometry("1000x650")
    
    configurar_estilos()
    
    # Datos de Prueba (solo si no existen)
    try:
        if not Activo.obtener_por_codigo("MESA-01"):
            a1 = Activo("MESA-01", "Mesas Plegables Blancas", 30, 30) 
            Activo.agregar_tipo_activo(a1)
        if not Activo.obtener_por_codigo("CABLE-05"):
            a2 = Activo("CABLE-05", "Cable de Extensión 5m", 50, 50)
            Activo.agregar_tipo_activo(a2)
    except Exception:
        pass


    # Título Principal
    title_frame = ttk.Frame(root, style='TFrame') 
    title_frame.pack(fill='x', pady=0)
    
    ttk.Label(title_frame, text="📦 INVENTARIO", 
             font=('Arial', 18, 'bold'), foreground='#2C3E50', anchor='center').pack(pady=15, fill='x')
    
    # Contenedor de Pestañas (Notebook)
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=10, expand=True, fill='both')
    
    # ------------------- PESTAÑA 1: INVENTARIO DE STOCK -------------------
    tab_inventario = ttk.Frame(notebook)
    notebook.add(tab_inventario, text='📊 Stock de Activos')
    
    button_frame_inv = ttk.Frame(tab_inventario)
    button_frame_inv.pack(pady=(15, 5), padx=10, fill='x')

    # Treeview (Tabla)
    columns_inv = ('codigo', 'nombre', 'total', 'disponibles', 'prestados')
    tree_inventario = ttk.Treeview(tab_inventario, columns=columns_inv, show='headings', height=15)
    
    tree_inventario.heading('codigo', text='CÓDIGO')
    tree_inventario.heading('nombre', text='ACTIVO')
    tree_inventario.heading('total', text='TOTAL')
    tree_inventario.heading('disponibles', text='DISPONIBLES')
    tree_inventario.heading('prestados', text='PRESTADOS')
    
    tree_inventario.column('codigo', width=100, anchor='center')
    tree_inventario.column('nombre', width=350)
    tree_inventario.column('total', width=80, anchor='center')
    tree_inventario.column('disponibles', width=100, anchor='center')
    tree_inventario.column('prestados', width=100, anchor='center')

    tree_inventario.pack(pady=10, padx=10, fill='both', expand=True)

    # ------------------- PESTAÑA 2: HISTORIAL DE PRÉSTAMOS -------------------
    tab_historial = ttk.Frame(notebook)
    notebook.add(tab_historial, text='📜 Historial de Préstamos')

    # Treeview (Historial)
    columns_hist = ('local', 'activo', 'cantidad', 'fecha_prestamo', 'estado')
    tree_historial = ttk.Treeview(tab_historial, columns=columns_hist, show='headings', height=15)
    
    tree_historial.heading('local', text='LOCAL / EVENTO')
    tree_historial.heading('activo', text='ACTIVO')
    tree_historial.heading('cantidad', text='CANTIDAD')
    tree_historial.heading('fecha_prestamo', text='FECHA')
    tree_historial.heading('estado', text='ESTADO')
    
    tree_historial.column('local', width=200)
    tree_historial.column('activo', width=250)
    tree_historial.column('cantidad', width=100, anchor='center')
    tree_historial.column('fecha_prestamo', width=150, anchor='center')
    tree_historial.column('estado', width=100, anchor='center')
    
    tree_historial.pack(pady=10, padx=10, fill='both', expand=True)
    
    # Frame de botones del Historial
    button_frame_hist = ttk.Frame(tab_historial)
    button_frame_hist.pack(pady=10, padx=10, fill='x')

    # --- BOTONES DE ACCIÓN (PESTAÑA 1) ---
    ttk.Button(button_frame_inv, text="➕ DAR DE ALTA ACTIVO", width=20,
              command=lambda: mostrar_formulario_activo(root, 'agregar', tree_inventario)).pack(side='left', padx=5)

    ttk.Button(button_frame_inv, text="➡️ PRÉSTAMO", width=15, style='Accent.TButton',
              command=lambda: mostrar_formulario_activo(root, 'prestar', tree_inventario, tree_historial)).pack(side='left', padx=5)

    ttk.Button(button_frame_inv, text="⬅️ DEVOLUCIÓN", width=15,
              command=lambda: mostrar_formulario_activo(root, 'devolver', tree_inventario, tree_historial)).pack(side='left', padx=5)
    
    # BOTÓN: ELIMINAR ACTIVO
    ttk.Button(button_frame_inv, text="🗑️ ELIMINAR ACTIVO", width=18,
              command=lambda: eliminar_activo_seleccionado(tree_inventario, root, tree_historial)).pack(side='left', padx=5)
    
    # Botón Exportar
    ttk.Button(button_frame_inv, text="📥 EXPORTAR A CSV (Excel)", width=25,
              command=generar_reporte_inventario_csv).pack(side='right', padx=5)

    # --- BOTONES DE LA PESTAÑA 2 (HISTORIAL) ---
    ttk.Button(button_frame_hist, text="🔄 Recargar Historial", width=20,
              command=lambda: cargar_historial(tree_historial)).pack(side='left', padx=5)

    # Cargar datos iniciales
    cargar_inventario(tree_inventario)
    cargar_historial(tree_historial)

    root.mainloop()

if __name__ == "__main__":
    main_window()