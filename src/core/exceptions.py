"""Excecoes customizadas do pipeline."""


class ConfigError(Exception):
    """Erro ao carregar ou validar a configuracao."""

    pass


class DataLoadError(Exception):
    """Erro ao carregar dados de uma fonte."""

    pass


class DataWriteError(Exception):
    """Erro ao escrever dados em um destino."""

    pass
