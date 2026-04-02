"""Modulo responsavel por carregar e validar a configuracao do pipeline."""

import os

import yaml

from src.core.exceptions import ConfigError


class ConfigLoader:
    """Carrega a configuracao a partir de um arquivo YAML."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "config",
                "config.yaml",
            )
        self._config_path = os.path.normpath(config_path)
        self._config: dict = {}
        self._load()

    def _load(self) -> None:
        """Carrega o arquivo YAML de configuracao."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise ConfigError(
                f"Arquivo de configuracao nao encontrado: {self._config_path}"
            ) from e
        except yaml.YAMLError as e:
            raise ConfigError(f"Erro ao interpretar o arquivo YAML: {e}") from e

        if not isinstance(self._config, dict):
            raise ConfigError("Configuracao invalida: esperado um dicionario YAML.")

    def get_dataset_config(self, dataset_id: str) -> dict:
        """Retorna a configuracao de um dataset pelo seu ID logico."""
        datasets = self._config.get("datasets", {})
        if dataset_id not in datasets:
            raise ConfigError(f"Dataset '{dataset_id}' nao encontrado na configuracao.")
        return datasets[dataset_id]

    def get_data_source_config(self, source_id: str) -> dict:
        """Retorna a configuracao de uma fonte de dados (repo git)."""
        sources = self._config.get("data_sources", {})
        if source_id not in sources:
            raise ConfigError(
                f"Data source '{source_id}' nao encontrado na configuracao."
            )
        return sources[source_id]

    @property
    def config(self) -> dict:
        """Retorna o dicionario completo de configuracao."""
        return self._config
