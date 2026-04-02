"""Ponto de entrada da aplicação - Composition Root."""

import os
import subprocess
import sys

from src.core.config import ConfigLoader
from src.data_io.data_io_manager import DataIOManager
from src.jobs.run_top_10 import RunTop10Job
from src.utils.logging_setup import setup_logging


def clone_dataset_if_needed(repo_url: str, target_dir: str) -> None:
    """Clona um repositório de dataset se o diretório não existir."""
    logger = setup_logging()
    if os.path.exists(target_dir):
        logger.info(f"Dataset já existe em: {target_dir}")
        return

    logger.info(f"Clonando dataset de {repo_url} para {target_dir}")
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    subprocess.run(
        ["git", "clone", repo_url, target_dir],
        check=True,
        capture_output=True,
        text=True,
    )
    logger.info(f"Dataset clonado com sucesso em: {target_dir}")


def main() -> None:
    """Função principal - Composition Root."""
    logger = setup_logging()
    logger.info("Iniciando aplicação...")

    # 1. Carregar configuração
    config = ConfigLoader()
    project_root = config.project_root

    # 2. Baixar datasets se necessário
    datasets_to_clone = [
        {
            "url": "https://github.com/infobarbosa/dataset-json-clientes",
            "target": os.path.join(
                project_root, "data", "input", "dataset-json-clientes"
            ),
        },
        {
            "url": "https://github.com/infobarbosa/datasets-csv-pedidos",
            "target": os.path.join(
                project_root, "data", "input", "datasets-csv-pedidos"
            ),
        },
    ]

    for ds in datasets_to_clone:
        clone_dataset_if_needed(ds["url"], ds["target"])

    # 3. Instanciar componentes (Injeção de Dependência)
    data_io = DataIOManager(config)

    # 4. Instanciar e executar o job
    top_n = config.get_pipeline_param("top_n", 10)
    job = RunTop10Job(data_io=data_io, top_n=top_n)
    job.run()


if __name__ == "__main__":
    sys.exit(main() or 0)
