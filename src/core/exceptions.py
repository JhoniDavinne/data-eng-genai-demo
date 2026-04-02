"""Exceções customizadas do pipeline."""


class ConfigError(Exception):
    """Erro ao carregar ou validar a configuração."""

    pass


class DataIOError(Exception):
    """Erro ao ler ou escrever dados."""

    pass
