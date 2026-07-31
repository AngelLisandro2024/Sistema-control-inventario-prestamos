# 📦 Sistema de Gestión de Inventario, Control de Activos y Préstamos

Aplicación de escritorio desarrollada en Python para la administración centralizada de inventarios, control de stock disponible y seguimiento en tiempo real del préstamo/devolución de activos a locales o arrendatarios. Diseñada con una arquitectura modular orientada a objetos (POO), persistencia en **SQLite** e interfaz gráfica con **Tkinter**.

---

## ✨ Características Principales

* **📊 Control de Stock en Tiempo Real:** Módulo para alta, edición y eliminación segura de activos (impide borrar ítems con unidades prestadas activas).
* **🔄 Gestión de Préstamos y Devoluciones:** Registro automatizado de salidas y entradas parciales o totales de equipos, actualizando instantáneamente las unidades disponibles.
* **📜 Historial Detallado de Movimientos:** Visualización diferenciada por estados (Prestado / Devuelto) con códigos de color dinámicos.
* **📥 Exportación a CSV (Excel):** Módulo para la generación y descarga de reportes de stock formateados para compatibilidad directa con Microsoft Excel u otras hojas de cálculo.
* **🖥️ Interfaz Gráfica Moderna (GUI):** Pestañas organizadas (`ttk.Notebook`), ventanas modales y validación estricta de datos de entrada.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3
* **Interfaz Gráfica:** Tkinter / `ttk` (Temas estilizados)
* **Base de Datos:** SQLite3 (Lógica embebida)
* **Exportación:** Modulo `csv` de Python
* **Arquitectura:** Programación Orientada a Objetos (POO) y separación por capas (Model / UI / DB Manager)

---

## 📁 Estructura del Proyecto

```text
Codigo_Sistema_Inventario-01/
├── activo_model.py         # Clase Activo, lógica CRUD y operaciones de préstamos/devoluciones
├── database_manager.py     # Manejo de conexión y creación del esquema SQLite (inventario.db)
├── interfaz_inventario.py   # Interfaz gráfica de usuario (GUI Tkinter) y componentes de UI
├── main_inventario.py     # Script ejecutable principal de pruebas e inicialización
├── reporte_csv.py          # Módulo para generación y exportación de reportes CSV
└── README.md               # Documentación del proyecto
```
⚙️ Guía de Ejecución
Clonar el Repositorio:

Bash

git clone [https://github.com/AngelLisandro2024/Codigo_Sistema_Inventario-01.git](https://github.com/AngelLisandro2024/Codigo_Sistema_Inventario-01.git)

cd Codigo_Sistema_Inventario-01

Ejecutar la Aplicación Principal:

Bash

python interfaz_inventario.py

(Nota: No requiere instalación de dependencias externas ya que utiliza la librería estándar de Python).

👨‍💻 Sobre el Desarrollador
Ángel Fernández | T.S.U en Informática

Desarrollador de software backend y creador de soluciones digitales enfocadas en funcionalidad, rendimiento y diseño accesible.
