import csv
from tkinter import filedialog, messagebox
from activo_model import Activo
from datetime import datetime
import os

def generar_reporte_inventario_csv():
    """Genera un archivo CSV con el STOCK ACTUAL del inventario."""
    
    default_filename = f"Reporte_Stock_Actual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_filename,
        title="Guardar Reporte de Stock Actual",
        filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
    )
    
    if not filepath:
        return

    try:
        # Usamos la función ya existente para obtener la lista de Activos (Stock)
        activos = Activo.obtener_todos()
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';') # Usar punto y coma
            
            # Encabezados CLAROS
            writer.writerow([
                'Código', 
                'Nombre del Activo', 
                'Total de Unidades', 
                'Unidades DISPONIBLES', 
                'Unidades PRESTADAS (Fuera de Stock)'
            ])
            
            for activo in activos:
                prestadas = activo.total_unidades - activo.disponibles
                
                writer.writerow([
                    activo.codigo, 
                    activo.nombre, 
                    activo.total_unidades, 
                    activo.disponibles, 
                    prestadas
                ])

        messagebox.showinfo("Éxito", f"Reporte de Stock Actual exportado correctamente a:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error de Exportación", f"Ocurrió un error al exportar el CSV: {e}")