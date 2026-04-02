"""DataIOManager - leitura e escrita de dados via IDs lógicos (Strategy Pattern)."""

import glob
import logging
import os

import pandas as pd

from src.core.config import ConfigLoader
from src.core.exceptions import DataIOError

logger = logging.getLogger("pipeline")


class DataIOManager:
    """Gerencia leitura e escrita de DataFrames usando IDs lógicos do catálogo."""

    def __init__(self, config: ConfigLoader) -> None:
        self._config = config

    def read(self, dataset_id: str) -> pd.DataFrame:
        """Lê um dataset pelo ID lógico e retorna um DataFrame."""
        ds_config = self._config.get_dataset_config(dataset_id)
        ds_path = self._config.get_dataset_path(dataset_id)
        ds_type = ds_config.get("type", "csv")

        logger.info(f"Lendo dataset '{dataset_id}' de: {ds_path}")

        if ds_type == "json":
            return self._read_json(ds_path)
        elif ds_type == "csv":
            separator = ds_config.get("separator", ",")
            return self._read_csv(ds_path, separator)
        else:
            raise DataIOError(f"Tipo de dataset não suportado: {ds_type}")

    def write(self, df: pd.DataFrame, dataset_id: str) -> None:
        """Escreve um DataFrame no caminho definido pelo ID lógico."""
        ds_config = self._config.get_dataset_config(dataset_id)
        ds_path = self._config.get_dataset_path(dataset_id)
        separator = ds_config.get("separator", ",")

        logger.info(f"Escrevendo dataset '{dataset_id}' em: {ds_path}")

        os.makedirs(ds_path, exist_ok=True)
        output_file = os.path.join(ds_path, f"{dataset_id}.csv")
        df.to_csv(output_file, sep=separator, index=False, encoding="utf-8")

        logger.info(f"Dataset '{dataset_id}' salvo com sucesso em: {output_file}")

    def _read_json(self, path: str) -> pd.DataFrame:
        """Lê um arquivo JSON lines (suporta .gz)."""
        if not os.path.exists(path):
            raise DataIOError(f"Arquivo JSON não encontrado: {path}")

        try:
            compression = "gzip" if path.endswith(".gz") else None
            return pd.read_json(
                path, lines=True, encoding="utf-8", compression=compression
            )
        except Exception as e:
            raise DataIOError(f"Erro ao ler JSON '{path}': {e}")

    def _read_csv(self, path: str, separator: str = ",") -> pd.DataFrame:
        """Lê um ou múltiplos arquivos CSV de um diretório."""
        if os.path.isfile(path):
            try:
                return pd.read_csv(path, sep=separator, encoding="utf-8")
            except Exception as e:
                raise DataIOError(f"Erro ao ler CSV '{path}': {e}")

        if not os.path.isdir(path):
            raise DataIOError(f"Caminho CSV não encontrado: {path}")

        csv_files = sorted(
            glob.glob(os.path.join(path, "*.csv"))
            + glob.glob(os.path.join(path, "*.csv.gz"))
        )
        if not csv_files:
            raise DataIOError(f"Nenhum arquivo CSV encontrado em: {path}")

        logger.info(f"Encontrados {len(csv_files)} arquivo(s) CSV em: {path}")

        frames = []
        for csv_file in csv_files:
            try:
                compression = "gzip" if csv_file.endswith(".gz") else None
                df = pd.read_csv(
                    csv_file,
                    sep=separator,
                    encoding="utf-8",
                    compression=compression,
                )
                frames.append(df)
            except Exception as e:
                raise DataIOError(f"Erro ao ler CSV '{csv_file}': {e}")

        return pd.concat(frames, ignore_index=True)
