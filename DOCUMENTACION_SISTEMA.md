# MoscatoSystem - Documentación Técnica

Este documento describe la arquitectura, la organización del código, las librerías utilizadas y el flujo general de MoscatoSystem, un sistema de gestión para restaurantes con roles de Administrador, Mesero y Cocinero.

## 1. Arquitectura del Sistema (Patrón MVC)

El sistema está construido siguiendo el patrón **MVC (Modelo-Vista-Controlador)**. Esto permite mantener el código altamente organizado, separando la lógica de la base de datos, la interfaz de usuario y la lógica de negocio.

- **Modelos (`src/models/`)**: Se encargan exclusivamente de la comunicación con la base de datos MySQL (consultas, inserciones, actualizaciones y borrados). No saben nada sobre la interfaz visual.
- **Vistas (`src/views/`)**: Contienen el código de la interfaz gráfica de usuario construida con CustomTkinter. Aquí se dibujan botones, tablas, mapas de mesas y monitores. No contienen lógica de negocio directa.
- **Controladores (`src/controllers/`)**: Actúan como puentes. Reciben las interacciones del usuario desde las Vistas, procesan la lógica necesaria y piden a los Modelos que actualicen la base de datos.
- **Core (Event Bus) (`src/core/event_bus.py`)**: El sistema usa un patrón de bus de eventos que permite que componentes separados se comuniquen en tiempo real sin estar acoplados (ej. Cuando la cocina termina un pedido, el evento viaja instantáneamente al panel del mesero para cambiar el color de la mesa).

## 2. Tecnologías y Librerías Utilizadas

El sistema fue desarrollado en **Python 3.10+**.

*   **CustomTkinter** (`customtkinter`): Librería principal de interfaz gráfica. Permite crear un diseño moderno (esquinas redondeadas, modo oscuro nativo, colores personalizables) superando al `tkinter` clásico.
*   **Tkinter** (`tkinter`): Utilizado como base subyacente para CustomTkinter, así como para el manejo de eventos (binds) y Scrollbars nativos cuando es necesario.
*   **MySQL Connector** (`mysql-connector-python`): Driver utilizado por los Modelos para conectarse al servidor de base de datos MySQL (XAMPP).
*   **Pillow** (`PIL`): Usado para el procesamiento de imágenes, logotipos y para generar dinámicamente iconos y gráficos en la interfaz sin necesidad de archivos externos.
*   **PyInstaller**: Usado para empaquetar y compilar todo el sistema Python en un único archivo `.exe` funcional en Windows.
*   **Otras utilidades estándar de Python**:
    *   `threading`: Para no congelar la pantalla al hacer ciertas lecturas o eventos.
    *   `datetime`: Manejo de tiempos (ej. cuánto demora un ticket en cocina).
    *   `ctypes`: Interacciones de bajo nivel con Windows, usado específicamente para detectar el Bloqueo de Mayúsculas (Caps Lock) por seguridad en el inicio de sesión.
    *   `winsound`: Reproducción nativa de alertas sonoras (la campanita de la cocina cuando entra un nuevo pedido).

## 3. Estructura y Distribución del Código

```text
MoscatoSystem/
│
├── main.py                     # Punto de entrada principal. Contiene el LoginWindow y la inicialización.
├── db_config.json              # Credenciales y host de conexión a la base de datos local.
├── moscato.sql                 # Respaldo y estructura de las tablas de la base de datos MySQL.
├── MoscatoSystem_OneFile.exe   # Ejecutable compilado del sistema listo para usar.
│
└── src/                        # Código fuente del sistema
    ├── core/
    │   └── event_bus.py        # Sistema de eventos en tiempo real.
    │
    ├── models/                 # MODELOS (Consultas DB)
    │   ├── admin/              # Modelos para la gestión administrativa.
    │   ├── auditoria/          # Modelo de registros de auditoría y cierre.
    │   ├── cocina/             # modelo_cocina.py (Pedidos activos).
    │   ├── mesas/              # modelo_mesas.py (Estado de las mesas: Libre, Ocupada, etc).
    │   ├── pedidos/            # model_mesero.py, modelo_pedido_actual.py.
    │   ├── productos/          # modelo_menu.py, imagenes_menu.py.
    │   └── usuarios/           # modelo_usuarios.py (Roles y credenciales).
    │
    ├── views/                  # VISTAS (Interfaz Gráfica)
    │   ├── admin/              # vista_admin.py (Dashboard del Administrador).
    │   ├── auditoria/          # auditoria_view.py (Historial).
    │   ├── cocina/             # vista_cocina.py (Monitor KDS de cocina).
    │   ├── mesas/              # vista_mesas.py (Plano visual de mesas con colores).
    │   └── pedidos/            # vista_mesero.py (Panel del Mesero), vista_pedido_actual.py.
    │
    └── controllers/            # CONTROLADORES (Lógica y validaciones)
        ├── admin/
        ├── auditoria/
        ├── cocina/             # controlador_cocina.py (Tiempo y estados del KDS).
        ├── mesas/              # controlador_mesas.py (Cambio de estados y sincronización).
        └── pedidos/            # controlador_mesero.py (Manejo integral del ciclo del pedido).
```

## 4. Flujos Principales del Sistema

1. **Flujo de Acceso (Login):**
   * El archivo `main.py` levanta el login y conecta a la base de datos (`DatabaseConnection`).
   * Valida estrictamente solo el uso de números para la contraseña e informa si las mayúsculas están activas (`ctypes`).
   * Según el rol recuperado (`Administrador`, `Cocinero`, `Mesero`), carga el Dashboard unificado apropiado y oculta el login.

2. **Flujo de un Pedido (Mesero -> Cocina):**
   * **Mesero (Creación):** Selecciona una mesa. El color pasa a "Atención" (Amarillo). Construye el pedido en `vista_pedido_actual.py` y presiona "A Cocina".
   * **Tránsito:** El controlador guarda el pedido en la BD y emite un evento `pedido.creado` mediante `event_bus.py`.
   * **Cocina (Recepción):** El monitor de cocina detecta el evento sin necesidad de recargar, suena una alerta sonora y muestra el nuevo ticket en rojo ("Enviado a cocina").
   * **Cocina (Preparación y Entrega):** El cocinero cambia el ticket a "En preparación" (Amarillo). Luego, cuando termina, presiona "Pedido Listo".
   * **Tránsito de vuelta:** Al marcar Listo, se emite el evento `pedido.listo`.
   * **Mesero (Entrega y Cierre):** El mapa de mesas en la pantalla del mesero pasa automáticamente a color rojo ("Ocupada") avisando que la comida está lista. El mesero entrega y finalmente oprime "Cerrar y Pagar", liberando la mesa ("Verde").

## 5. Compilación y Mantenimiento

Para generar el archivo ejecutable (`.exe`) desde el código fuente después de hacer alguna actualización o edición en Python:

1. Se utiliza el entorno virtual incluido o la instalación global de Python.
2. Se ejecuta el comando de compilación mediante PyInstaller:
   ```cmd
   python -m PyInstaller --noconfirm --onefile --windowed --name "MoscatoSystem" main.py
   ```
   * `--onefile`: Empaqueta todo el proyecto en un solo archivo `.exe`.
   * `--windowed`: Elimina la consola negra (cmd) que aparece detrás de las interfaces gráficas.
   * `main.py`: Es el archivo de entrada donde PyInstaller comienza a leer todas las librerías y dependencias.

