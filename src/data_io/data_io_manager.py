"""Modulo responsavel pela leitura e escrita de dados (Strategy Pattern)."""

import csv
import glob
import json
import logging
import os

from src.core.config import ConfigLoader
from src.core.exceptions import DataLoadError, DataWriteError

logger = logging.getLogger(__name__)


class DataIOManager:
    """Gerencia leitura e escrita de dados baseado no catalogo de configuracao."""

    def __init__(self, config_loader: ConfigLoader, base_path: str = None):
        self._config_loader = config_loader
        if base_path is None:
            base_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", ".."
            )
        self._base_path = os.path.normpath(base_path)

    def _resolve_path(self, relative_path: str) -> str:
        """Resolve um caminho relativo em relacao ao base_path."""
        return os.path.normpath(os.path.join(self._base_path, relative_path))

    def read(self, dataset_id: str) -> list[dict]:
        """Le um dataset pelo seu ID logico e retorna uma lista de dicts."""
        ds_config = self._config_loader.get_dataset_config(dataset_id)
        ds_type = ds_config.get("type", "csv")
        raw_path = ds_config.get("path", "")
        resolved_path = self._resolve_path(raw_path)

        if ds_type == "json":
            return self._read_json(resolved_path)
        elif ds_type == "csv":
            separator = ds_config.get("separator", ",")
            return self._read_csv(resolved_path, separator)
        else:
            raise DataLoadError(f"Tipo de dataset desconhecido: {ds_type}")

    def write(self, dataset_id: str, data: list[dict]) -> None:
        """Escreve uma lista de dicts como CSV no caminho do dataset."""
        ds_config = self._config_loader.get_dataset_config(dataset_id)
        raw_path = ds_config.get("path", "")
        separator = ds_config.get("separator", ",")
        resolved_path = self._resolve_path(raw_path)

        self._write_csv(resolved_path, data, separator)

    def _read_json(self, path: str) -> list[dict]:
        """Le um arquivo JSON Lines (uma linha JSON por registro)."""
        if not os.path.isfile(path):
            raise DataLoadError(f"Arquivo JSON nao encontrado: {path}")

        records: list[dict] = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_number, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        records.append(json.loads(stripped))
                    except json.JSONDecodeError as e:
                        logger.warning(
                            "Linha %d ignorada em %s: %s", line_number, path, e
                        )
        except OSError as e:
            raise DataLoadError(f"Erro ao ler arquivo JSON {path}: {e}") from e

        logger.info("Lidos %d registros de %s", len(records), path)
        return records

    def _read_csv(self, path: str, separator: str) -> list[dict]:
        """Le arquivos CSV de um diretorio ou arquivo unico."""
        records: list[dict] = []

        if os.path.isfile(path):
            files = [path]
        elif os.path.isdir(path):
            files = sorted(glob.glob(os.path.join(path, "*.csv")))
            if not files:
                raise DataLoadError(
                    f"Nenhum arquivo CSV encontrado no diretorio: {path}"
                )
        else:
            raise DataLoadError(f"Caminho CSV nao encontrado: {path}")

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f, delimiter=separator)
                    for row in reader:
                        records.append(dict(row))
            except OSError as e:
                raise DataLoadError(f"Erro ao ler arquivo CSV {filepath}: {e}") from e

        logger.info("Lidos %d registros CSV de %s", len(records), path)
        return records

    def _write_csv(self, path: str, data: list[dict], separator: str) -> None:
        """Escreve uma lista de dicts como arquivo CSV."""
        if not data:
            logger.warning("Nenhum dado para escrever em %s", path)
            return

        try:
            os.makedirs(path, exist_ok=True)
            output_file = os.path.join(path, "top_10_clientes.csv")
            fieldnames = list(data[0].keys())

            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=separator)
                writer.writeheader()
                writer.writerows(data)

            logger.info("Escritos %d registros em %s", len(data), output_file)
        except OSError as e:
            raise DataWriteError(f"Erro ao escrever dados em {path}: {e}") from e
