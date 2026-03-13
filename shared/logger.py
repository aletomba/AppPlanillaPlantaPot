import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs") -> None:
    """Configura logging con salida a archivo y consola para toda la aplicación."""
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        # Ya fue inicializado (p.ej. en pruebas)
        return
    root.setLevel(logging.DEBUG)

    # Silenciar loggers ruidosos de terceros
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Handler de archivo: DEBUG y superior, rotación 1 MB × 5 archivos
    fh = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Handler de consola: WARNING y superior
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    root.addHandler(fh)
    root.addHandler(ch)
