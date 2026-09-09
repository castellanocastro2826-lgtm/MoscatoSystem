import os
import json
import logging

CONFIG_FILE = "db_config.json"

def load_db_config():
    """Carga la configuración de la base de datos y la aplica al entorno."""
    if not os.path.exists(CONFIG_FILE):
        logging.info("Archivo de configuración de base de datos no encontrado. Se usarán valores por defecto.")
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            for key, value in config.items():
                os.environ[key] = str(value)
        logging.info("Configuración de base de datos cargada exitosamente.")
    except Exception as e:
        logging.error(f"Error al cargar la configuración de la base de datos: {e}")

def save_db_config(host, port, user, password, database):
    """Guarda la configuración de la base de datos en un archivo JSON."""
    config = {
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_NAME": database
    }
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        
        # Actualizar entorno inmediatamente
        for key, value in config.items():
            os.environ[key] = str(value)
        
        logging.info("Configuración de base de datos guardada exitosamente.")
        return True, "Configuración guardada correctamente."
    except Exception as e:
        logging.error(f"Error al guardar la configuración: {e}")
        return False, f"Error al guardar: {e}"

def get_current_config():
    """Obtiene la configuración actual (de variables de entorno o archivo)."""
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "3306"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "moscato_db")
    }
