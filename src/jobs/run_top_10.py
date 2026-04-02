"""Job de orquestracao do pipeline Top 10 Clientes."""

import logging

from src.data_io.data_io_manager import DataIOManager
from src.transforms.vendas_transforms import VendasTransforms

logger = logging.getLogger(__name__)


class RunTop10Job:
    """Orquestra o pipeline que identifica os Top 10 Clientes por compras."""

    def __init__(self, data_io: DataIOManager):
        self._data_io = data_io
        self._transforms = VendasTransforms()

    def execute(self) -> list[dict]:
        """Executa o pipeline completo.

        Fluxo:
            1. Ler pedidos (pedidos_bronze)
            2. Calcular valor total por pedido
            3. Agregar por cliente
            4. Selecionar top 10
            5. Enriquecer com dados de clientes (clientes_bronze)
            6. Escrever resultado (top_10_clientes)

        Returns:
            Lista dos top 10 clientes enriquecidos.
        """
        logger.info("Iniciando pipeline Top 10 Clientes...")

        logger.info("Lendo pedidos...")
        pedidos = self._data_io.read("pedidos_bronze")
        logger.info("Total de pedidos lidos: %d", len(pedidos))

        logger.info("Calculando valor total por pedido...")
        pedidos_com_total = self._transforms.calcular_valor_total(pedidos)

        logger.info("Agregando por cliente...")
        agregado = self._transforms.agregar_por_cliente(pedidos_com_total)
        logger.info("Total de clientes unicos: %d", len(agregado))

        logger.info("Selecionando Top 10 clientes...")
        top10 = self._transforms.top_10_clientes(agregado)

        logger.info("Enriquecendo com dados de clientes...")
        clientes = self._data_io.read("clientes_bronze")
        logger.info("Total de clientes carregados: %d", len(clientes))

        top10_enriquecido = self._transforms.enriquecer_com_clientes(top10, clientes)

        logger.info("Salvando resultado...")
        self._data_io.write("top_10_clientes", top10_enriquecido)

        logger.info("Pipeline Top 10 Clientes concluido com sucesso!")
        return top10_enriquecido
