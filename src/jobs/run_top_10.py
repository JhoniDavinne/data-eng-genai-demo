"""Job de orquestração do pipeline Top 10 Clientes."""

import logging

from src.data_io.data_io_manager import DataIOManager
from src.transforms.vendas_transforms import VendasTransforms

logger = logging.getLogger("pipeline")


class RunTop10Job:
    """Orquestra o pipeline de identificação dos Top 10 Clientes."""

    def __init__(self, data_io: DataIOManager, top_n: int = 10) -> None:
        self._data_io = data_io
        self._top_n = top_n
        self._transforms = VendasTransforms()

    def run(self) -> None:
        """Executa o pipeline completo."""
        logger.info("=== Iniciando pipeline Top 10 Clientes ===")

        # 1. Leitura dos dados
        logger.info("Etapa 1: Leitura dos dados")
        df_clientes = self._data_io.read("clientes")
        df_pedidos = self._data_io.read("pedidos")

        logger.info(f"Clientes carregados: {len(df_clientes)} registros")
        logger.info(f"Pedidos carregados: {len(df_pedidos)} registros")

        # 2. Calcular valor total por pedido
        logger.info("Etapa 2: Calculando valor total por pedido")
        df_pedidos = self._transforms.calcular_valor_total(df_pedidos)

        # 3. Agregar por cliente
        logger.info("Etapa 3: Agregando por cliente")
        df_agregado = self._transforms.agregar_por_cliente(df_pedidos)

        # 4. Ranking Top N
        logger.info(f"Etapa 4: Gerando ranking Top {self._top_n}")
        df_ranking = self._transforms.ranking_top_n(df_agregado, self._top_n)

        # 5. Enriquecer com dados de clientes
        logger.info("Etapa 5: Enriquecendo com dados de clientes")
        df_resultado = self._transforms.enriquecer_com_clientes(df_ranking, df_clientes)

        logger.info(f"Top {self._top_n} Clientes:")
        logger.info(f"\n{df_resultado.to_string(index=False)}")

        # 6. Salvar resultado
        logger.info("Etapa 6: Salvando resultado")
        self._data_io.write(df_resultado, "top_10_clientes")

        logger.info("=== Pipeline finalizado com sucesso ===")
