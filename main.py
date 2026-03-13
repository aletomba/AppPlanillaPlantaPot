import logging
import os
import sys
import requests
from shared.logger import setup_logging
from presentation.app import APIViewerApp
from ttkthemes import ThemedTk

logger = logging.getLogger(__name__)


def detect_base_url() -> str:
    """Detecta automáticamente el puerto donde corre la API.

    Prioridad:
    1) Variable de entorno `API_BASE_URL` si está seteada
    2) Prueba los puertos más comunes de .NET (http y https)
    3) Fallback a http://localhost:5261/api
    """
    env_url = os.environ.get("API_BASE_URL")
    if env_url:
        return env_url.rstrip("/")

    candidates = [
        "http://localhost:5261/api",
        "http://localhost:5000/api",
        "http://localhost:5001/api",
        "http://localhost:5100/api",
        "http://localhost:5200/api",
        "http://localhost:8080/api",
        "http://localhost:8000/api",
        "https://localhost:7206/api",
        "https://localhost:7000/api",
        "https://localhost:7001/api",
        "https://localhost:7100/api",
    ]

    for base_url in candidates:
        try:
            probe_url = f"{base_url}/cliente"
            resp = requests.get(probe_url, timeout=2, verify=False)
            if resp.status_code < 500:
                logger.info("[API] Conectado en: %s", base_url)
                return base_url
        except Exception:
            continue

    logger.warning("[API] No se encontró la API en ningún puerto conocido. Usando fallback.")
    return "http://localhost:5261/api"

def main():
    setup_logging()

    def _handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logging.getLogger(__name__).critical(
            "Excepción no capturada", exc_info=(exc_type, exc_value, exc_tb)
        )

    sys.excepthook = _handle_exception

    root = ThemedTk(theme="arc")
    base_url = detect_base_url()
    app = APIViewerApp(root, base_url=base_url)
    root.mainloop()

if __name__ == "__main__":
    main()