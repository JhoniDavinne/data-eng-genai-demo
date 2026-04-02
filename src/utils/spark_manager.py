import logging

from pyspark.sql import SparkSession

logger = logging.getLogger("pipeline")


class SparkManager:
    """Factory para criar e gerenciar SparkSession."""

    def __init__(self, app_name: str, master: str) -> None:
        self._app_name = app_name
        self._master = master
        self._spark: SparkSession | None = None

    def obter_sessao(self) -> SparkSession:
        """Cria ou retorna a SparkSession existente."""
        if self._spark is None:
            logger.info(
                "Criando SparkSession: app_name=%s, master=%s",
                self._app_name,
                self._master,
            )
            self._spark = (
                SparkSession.builder.appName(self._app_name)
                .master(self._master)
                .getOrCreate()
            )
        return self._spark

    def encerrar(self) -> None:
        """Encerra a SparkSession."""
        if self._spark is not None:
            logger.info("Encerrando SparkSession.")
            self._spark.stop()
            self._spark = None
