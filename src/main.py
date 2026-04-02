"""Ponto de entrada da aplicação — Composition Root.

Instancia e injeta todas as dependências (ConfigLoader, SparkManager,
DataIOManager) no job de pipeline.
"""

import os
import sys

from src.core.config import ConfigLoader
from src.data_io.data_io_manager import DataIOManager
from src.jobs.run_top_10 import RunTop10Job
from src.utils.logging_setup import configurar_logging
from src.utils.spark_manager import SparkManager


def main() -> None:
    logger = configurar_logging()

    # Raiz do projeto (diretório que contém config/ e src/)
    raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(raiz_projeto, "config", "config.yaml")

    logger.info("Carregando configuração de: %s", config_path)
    config = ConfigLoader(config_path)

    # SparkManager
    app_name = config.obter("spark.app_name", "PipelineApp")
    master = config.obter("spark.master", "local[*]")
    spark_manager = SparkManager(app_name=app_name, master=master)

    try:
        spark = spark_manager.obter_sessao()

        # DataIOManager
        catalogo = config.obter("catalogo", {})
        saida = config.obter("saida", {})
        data_io = DataIOManager(
            spark=spark,
            catalogo=catalogo,
            saida=saida,
            raiz_projeto=raiz_projeto,
        )

        # Job
        job = RunTop10Job(data_io=data_io)
        job.executar()

    except Exception as e:
        logger.error("Erro na execução do pipeline: %s", e)
        sys.exit(1)
    finally:
        spark_manager.encerrar()


if __name__ == "__main__":
    main()
