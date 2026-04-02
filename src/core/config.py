import os
from typing import Any, Dict

import yaml

from src.core.exceptions import ConfigError


class ConfigLoader:
    """Carrega e fornece acesso à configuração do pipeline."""

    def __init__(self, config_path: str) -> None:
        self._config_path = config_path
        self._config: Dict[str, Any] = self._carregar()

    def _carregar(self) -> Dict[str, Any]:
        if not os.path.exists(self._config_path):
            raise ConfigError(
                f"Arquivo de configuração não encontrado: {self._config_path}"
            )

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Erro ao parsear config.yaml: {e}")

        if config is None:
            raise ConfigError("Arquivo de configuração está vazio.")

        return config

    def obter(self, chave: str, padrao: Any = None) -> Any:
        """Obtém um valor de configuração por chave com notação de ponto."""
        partes = chave.split(".")
        valor: Any = self._config
        for parte in partes:
            if isinstance(valor, dict):
                valor = valor.get(parte)
            else:
                return padrao
            if valor is None:
                return padrao
        return valor

    @property
    def config(self) -> Dict[str, Any]:
        return self._config
