# Moscato System - Sistema de Gestión de Restaurante

Sistema integral de gestión de restaurantes para escritorio desarrollado en **Python** con interfaz gráfica moderna (**CustomTkinter**) y base de datos relacional (**MySQL**). El sistema sigue el patrón de arquitectura **Modelo-Vista-Controlador (MVC)** y está diseñado para soportar operación tanto local como en red de área local (LAN).

---

##  Características Principales

* **Control de Acceso y Roles de Usuario:**
  * **Administrador:** Gestión integral del personal/usuarios, cartas de productos/categorías, configuración de mesas, consulta de reportes y auditoría del sistema.
  * **Mesero:** Gestión y apertura de mesas, toma de pedidos en tiempo real, adición de notas especiales y seguimiento del estado de comandas.
  * **Cocinero (KDS - Kitchen Display System):** Visualización interactiva de pedidos pendientes, preparación y cambio de estados en cocina.
* **Módulo de Auditoría:** Registro pormenorizado de acciones del sistema (creación, edición y eliminación de datos).
* **Reportes y Análisis:** Exportación y visualización de pedidos, ventas y rendimiento con soporte para Excel (`openpyxl`).
* **Configuración LAN y Base de Datos Dinámica:** Detección y configuración de conexión a base de datos centralizada mediante interfaz gráfica.

---

## 🛠️ Tecnologías y Requisitos

* **Lenguaje:** Python 3.10 o superior.
* **Interfaz de Usuario:** CustomTkinter & Tkinter.
* **Base de Datos:** MySQL 8.0+ / MariaDB (compatible con XAMPP o MySQL Server).
* **Librerías principales:**
  * `customtkinter` (UI moderna)
  * `mysql-connector-python` (Driver oficial MySQL)
  * `pillow` (Manipulación de imágenes e iconos)
  * `openpyxl` (Generación de hojas de cálculo)
  * `darkdetect` (Detección de modo claro/oscuro)

---

## 🚀 Guía de Instalación y Ejecución (Código Fuente)

### 1. Requisitos Previos
Asegúrese de tener instalados:
* [Python 3.10+](https://www.python.org/downloads/) (marcar la casilla *"Add python.exe to PATH"* durante la instalación).
* Servidor MySQL activo (por ejemplo, mediante [XAMPP](https://www.apachefriends.org/) iniciando el servicio **MySQL**).

### 2. Configurar la Base de Datos
1. Abra su gestor de bases de datos preferido (phpMyAdmin, MySQL Workbench o consola MySQL).
2. Cree la base de datos e importe el archivo `moscato.sql` ubicado en la raíz del proyecto:
   * **Vía phpMyAdmin:** Cree la base de datos `moscato_db` o vaya a la pestaña **Importar**, seleccione el archivo `moscato.sql` y haga clic en **Importar**.
   * **Vía consola MySQL:**
     ```bash
     mysql -u root -p < moscato.sql
     ```
   *(El script creará automáticamente las tablas, índices y datos iniciales de prueba: mesas, categorías, productos y usuarios).*

### 3. Configurar el Entorno Virtual de Python
Abra una terminal o PowerShell en la carpeta raíz del proyecto y ejecute:

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Windows (CMD):
.\venv\Scripts\activate.bat
# En Linux / macOS:
source venv/bin/activate

# Instalar dependencias requeridas
pip install -r requirements.txt
```

### 4. Configuración de Conexión (`db_config.json`)
El sistema utiliza el archivo `db_config.json` para conectarse a la base de datos. Por defecto viene preconfigurado para un entorno local:
```json
{
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_USER": "root",
    "DB_PASSWORD": "",
    "DB_NAME": "moscato_db"
}
```
*Si su servidor MySQL tiene una contraseña o puerto diferente, edite los valores correspondientes en `db_config.json`.*

### 5. Iniciar la Aplicación
Con el entorno virtual activado y MySQL en ejecución:
```bash
python main.py
```

---

## 🔑 Credenciales de Acceso por Defecto

El script `moscato.sql` incluye usuarios preconfigurados para pruebas:

| Rol | Usuario | Contraseña | Descripción / Acceso |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `123` | Control total, auditoría, menú, usuarios, mesas y reportes |
| **Mesero** | `mesero1` | `0000` | Asignación de mesas y toma de pedidos |
| **Mesero 2** | `mesero2` | `0000` | Acceso alternativo para meseros |
| **Cocinero** | `cocinero1` | `0000` | Monitor de cocina y comanda de pedidos |
| **Cocinero 2** | `cocinero2` | `0000` | Acceso secundario de cocina |

---

## 📁 Estructura del Proyecto

```text
Proyecto_v.3/
├── docs/                       # Documentación técnica y guías de red LAN
├── Instalador/                 # Instalador ejecutable compilado (.exe)
├── src/                        # Código fuente del sistema
│   ├── assets/                 # Recursos visuales, imágenes y estilos
│   ├── controllers/            # Controladores del patrón MVC
│   │   ├── admin/              # Lógica de administración general
│   │   ├── auditoria/          # Lógica de registro y auditoría
│   │   ├── cocina/             # Lógica del monitor de cocina
│   │   ├── mesas/              # Control y estado de mesas
│   │   ├── pedidos/            # Gestión de órdenes y análisis
│   │   ├── productos/          # Gestión de menú y catálogo
│   │   └── usuarios/           # Gestión de cuentas y credenciales
│   ├── core/                   # Inicialización y ventana principal de la app
│   ├── models/                 # Modelos de datos y consultas SQL
│   ├── reports/                # Lógica de exportación de reportes
│   ├── utils/                  # Utilidades (rutas, configuración DB, etc.)
│   └── views/                  # Vistas e interfaces gráficas (CustomTkinter)
├── tests/                      # Pruebas unitarias
├── db_config.json              # Configuración activa de base de datos
├── db_config.example.json      # Plantilla de configuración
├── instalador.iss              # Script de compilación de instalador (Inno Setup)
├── main.py                     # Punto de entrada principal
├── moscato.sql                 # Script SQL para estructura y datos iniciales
├── MoscatoSystem.spec          # Archivo de especificación para PyInstaller
├── moscato_logo.ico            # Ícono oficial de la aplicación
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación general del proyecto
```

---

## 📦 Distribución y Ejecutable

Para empaquetar la aplicación en un ejecutable independiente de Windows:
1. **PyInstaller:**
   ```bash
   pyinstaller MoscatoSystem.spec
   ```
2. **Inno Setup:**
   Compile el script `instalador.iss` con Inno Setup Compiler para generar el instalador en la carpeta `Instalador/Instalar_Moscato.exe`.

