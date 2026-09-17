import logging
from src.core.app import MoscatoApp
from src.utils.db_config import load_db_config

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log", mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def main() -> None:
    setup_logging()
    logging.info("Iniciando aplicación Moscato...")
    
    # Cargar configuración de base de datos y LAN
    load_db_config()
    

    app = MoscatoApp()
    app.mainloop()

if __name__ == "__main__":
    main()