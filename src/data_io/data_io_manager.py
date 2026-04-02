import logging
from typing import Any, Dict, Optional

from pyspark.sql import DataFrame, SparkSession

from src.core.exceptions import DataIOError

logger = logging.getLogger("pipeline")


class DataIOManager:
    """Gerencia leitura e escrita de dados utilizando Strategy Pattern.

    Resolve IDs lógicos (ex: 'clientes', 'pedidos') para caminhos
    físicos e formatos definidos no catálogo de configuração.
    """

    def __init__(
        self,
        spark: SparkSession,
        catalogo: Dict[str, Any],
        saida: Dict[str, Any],
        raiz_projeto: str,
    ) -> None:
        self._spark = spark
        self._catalogo = catalogo
        self._saida = saida
        self._raiz_projeto = raiz_projeto

    def _resolver_caminho(self, caminho_relativo: str) -> str:
        """Resolve um caminho relativo à raiz do projeto."""
        import os

        return os.path.join(self._raiz_projeto, caminho_relativo)

    def ler(self, dataset_id: str) -> DataFrame:
        """Lê um dataset pelo seu ID lógico no catálogo."""
        if dataset_id not in self._catalogo:
            raise DataIOError(f"Dataset '{dataset_id}' não encontrado no catálogo.")

        entrada = self._catalogo[dataset_id]
        formato = entrada["formato"]
        caminho = self._resolver_caminho(entrada["caminho"])
        opcoes: Optional[Dict[str, str]] = entrada.get("opcoes")

        logger.info(
            "Lendo dataset '%s' (formato=%s) de: %s",
            dataset_id,
            formato,
            caminho,
        )

        reader = self._spark.read.format(formato)
        if opcoes:
            for chave, valor in opcoes.items():
                reader = reader.option(chave, valor)

        return reader.load(caminho)

    def escrever(
        self,
        df: DataFrame,
        dataset_id: str,
        modo: str = "overwrite",
    ) -> None:
        """Escreve um DataFrame no destino definido na configuração de saída."""
        if dataset_id not in self._saida:
            raise DataIOError(
                f"Destino de saída '{dataset_id}' não encontrado na configuração."
            )

        destino = self._saida[dataset_id]
        formato = destino["formato"]
        caminho = self._resolver_caminho(destino["caminho"])

        logger.info(
            "Escrevendo dataset '%s' (formato=%s) em: %s",
            dataset_id,
            formato,
            caminho,
        )

        df.write.format(formato).mode(modo).save(caminho)
