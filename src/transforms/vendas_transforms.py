from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


class VendasTransforms:
    """Transformações puras sobre DataFrames de vendas.

    Todas as funções recebem DataFrames e retornam DataFrames,
    garantindo testabilidade total sem necessidade de I/O.
    """

    @staticmethod
    def calcular_valor_total(df_pedidos: DataFrame) -> DataFrame:
        """Adiciona a coluna VALOR_TOTAL = VALOR_UNITARIO * QUANTIDADE."""
        return df_pedidos.withColumn(
            "VALOR_TOTAL",
            F.col("VALOR_UNITARIO").cast("double") * F.col("QUANTIDADE").cast("int"),
        )

    @staticmethod
    def agregar_por_cliente(df_pedidos: DataFrame) -> DataFrame:
        """Agrega o valor total de compras por ID_CLIENTE."""
        return df_pedidos.groupBy("ID_CLIENTE").agg(
            F.sum("VALOR_TOTAL").alias("TOTAL_COMPRAS"),
            F.count("ID_PEDIDO").alias("QTD_PEDIDOS"),
        )

    @staticmethod
    def rankear_top_n(df_agregado: DataFrame, n: int = 10) -> DataFrame:
        """Rankeia os clientes por TOTAL_COMPRAS e retorna os top N."""
        window = Window.orderBy(F.col("TOTAL_COMPRAS").desc())
        return (
            df_agregado.withColumn("RANKING", F.row_number().over(window))
            .filter(F.col("RANKING") <= n)
            .orderBy("RANKING")
        )

    @staticmethod
    def enriquecer_com_clientes(
        df_ranking: DataFrame, df_clientes: DataFrame
    ) -> DataFrame:
        """Faz join do ranking com dados de clientes para enriquecer o resultado."""
        return df_ranking.join(
            df_clientes.select(
                F.col("id").alias("ID_CLIENTE"),
                F.col("nome"),
                F.col("email"),
            ),
            on="ID_CLIENTE",
            how="left",
        ).orderBy("RANKING")
