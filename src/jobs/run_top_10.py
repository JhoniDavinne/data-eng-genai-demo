import logging

from src.data_io.data_io_manager import DataIOManager
from src.transforms.vendas_transforms import VendasTransforms

logger = logging.getLogger("pipeline")


class RunTop10Job:
    """Orquestra o pipeline de identificação dos Top 10 Clientes."""

    def __init__(self, data_io: DataIOManager) -> None:
        self._data_io = data_io
        self._transforms = VendasTransforms()

    def executar(self) -> None:
        """Executa o pipeline completo."""
        logger.info("Iniciando pipeline Top 10 Clientes...")

        # 1. Leitura dos dados
        logger.info("Lendo dados de pedidos...")
        df_pedidos = self._data_io.ler("pedidos")

        logger.info("Lendo dados de clientes...")
        df_clientes = self._data_io.ler("clientes")

        # 2. Transformações
        logger.info("Calculando valor total por pedido...")
        df_com_total = self._transforms.calcular_valor_total(df_pedidos)

        logger.info("Agregando por cliente...")
        df_agregado = self._transforms.agregar_por_cliente(df_com_total)

        logger.info("Rankeando Top 10...")
        df_top_10 = self._transforms.rankear_top_n(df_agregado, n=10)

        logger.info("Enriquecendo com dados de clientes...")
        df_resultado = self._transforms.enriquecer_com_clientes(df_top_10, df_clientes)

        # 3. Escrita do resultado
        logger.info("Salvando resultado...")
        self._data_io.escrever(df_resultado, "top_10_clientes")

        logger.info("Pipeline Top 10 Clientes finalizado com sucesso!")
