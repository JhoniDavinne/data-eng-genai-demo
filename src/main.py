"""Ponto de entrada da aplicacao (Composition Root).

Responsavel por:
    - Configurar logging
    - Carregar configuracao
    - Baixar datasets de exemplo (se necessario)
    - Instanciar dependencias (ConfigLoader, DataIOManager)
    - Injetar dependencias no job e executa-lo
"""

import logging
import os
import subprocess
import sys

from src.core.config import ConfigLoader
from src.data_io.data_io_manager import DataIOManager
from src.jobs.run_top_10 import RunTop10Job


def setup_logging() -> None:
    """Configura o sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def download_datasets(config_loader: ConfigLoader, base_path: str) -> None:
    """Baixa os datasets de exemplo via git clone, se ainda nao existirem."""
    logger = logging.getLogger(__name__)
    sources = config_loader.config.get("data_sources", {})

    for source_id, source_config in sources.items():
        repo_url = source_config["repo"]
        dest = os.path.normpath(os.path.join(base_path, source_config["dest"]))

        if os.path.isdir(dest):
            logger.info(
                "Dataset '%s' ja existe em %s. Pulando download.",
                source_id,
                dest,
            )
            continue

        logger.info("Baixando dataset '%s' de %s...", source_id, repo_url)
        try:
            subprocess.run(
                ["git", "clone", repo_url, dest],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("Dataset '%s' baixado com sucesso em %s.", source_id, dest)
        except subprocess.CalledProcessError as e:
            logger.error(
                "Erro ao baixar dataset '%s': %s\n%s",
                source_id,
                e.stdout,
                e.stderr,
            )
            raise


def main() -> None:
    """Funcao principal do pipeline."""
    setup_logging()
    logger = logging.getLogger(__name__)

    base_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )
    logger.info("Diretorio base: %s", base_path)

    config_path = os.path.join(base_path, "config", "config.yaml")
    config_loader = ConfigLoader(config_path=config_path)
    logger.info("Configuracao carregada com sucesso.")

    download_datasets(config_loader, base_path)

    data_io = DataIOManager(config_loader=config_loader, base_path=base_path)

    job = RunTop10Job(data_io=data_io)
    resultado = job.execute()

    logger.info("=== Top 10 Clientes ===")
    for cliente in resultado:
        logger.info(
            "#%s - %s (%s) - R$ %.2f",
            cliente["RANKING"],
            cliente["NOME"],
            cliente["EMAIL"],
            float(cliente["VALOR_TOTAL_COMPRAS"]),
        )


if __name__ == "__main__":
    main()
