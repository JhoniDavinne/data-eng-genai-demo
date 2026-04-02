"""ConfigLoader - carrega e valida o config.yaml."""

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.core.exceptions import ConfigError


class ConfigLoader:
    """Carrega a configuração do pipeline a partir de um arquivo YAML."""

    def __init__(self, config_path: str | None = None) -> None:
        if config_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            config_path = str(project_root / "config" / "config.yaml")

        self._config_path = config_path
        self._config: Dict[str, Any] = self._load()
        self._project_root = str(Path(self._config_path).resolve().parent.parent)

    def _load(self) -> Dict[str, Any]:
        """Carrega o arquivo YAML."""
        if not os.path.exists(self._config_path):
            raise ConfigError(
                f"Arquivo de configuração não encontrado: {self._config_path}"
            )

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Erro ao parsear o YAML: {e}")

        if not config:
            raise ConfigError("Arquivo de configuração está vazio.")

        if "datasets" not in config:
            raise ConfigError("Seção 'datasets' não encontrada no config.")

        return config

    @property
    def project_root(self) -> str:
        """Retorna o caminho raiz do projeto."""
        return self._project_root

    def get_dataset_config(self, dataset_id: str) -> Dict[str, Any]:
        """Retorna a configuração de um dataset pelo ID lógico."""
        datasets = self._config.get("datasets", {})
        if dataset_id not in datasets:
            raise ConfigError(
                f"Dataset '{dataset_id}' não encontrado no catálogo de configuração."
            )
        return datasets[dataset_id]

    def get_dataset_path(self, dataset_id: str) -> str:
        """Retorna o caminho absoluto de um dataset."""
        ds_config = self.get_dataset_config(dataset_id)
        relative_path = ds_config["path"]
        return os.path.join(self._project_root, relative_path)

    def get_pipeline_param(self, param: str, default: Any = None) -> Any:
        """Retorna um parâmetro do pipeline."""
        return self._config.get("pipeline", {}).get(param, default)

    def get_dataset_sources(self) -> List[Dict[str, str]]:
        """Retorna a lista de sources (url + target absoluto) dos datasets."""
        sources = []
        for ds_config in self._config.get("datasets", {}).values():
            source = ds_config.get("source")
            if source:
                sources.append(
                    {
                        "url": source["url"],
                        "target": os.path.join(self._project_root, source["target"]),
                    }
                )
        return sources
