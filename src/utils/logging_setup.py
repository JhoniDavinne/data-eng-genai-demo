import logging
import sys


def configurar_logging(nivel: str = "INFO") -> logging.Logger:
    """Configura e retorna o logger padrão do pipeline."""
    logger = logging.getLogger("pipeline")
    logger.setLevel(getattr(logging, nivel.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, nivel.upper(), logging.INFO))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
