"""Lógica pura de transformação para o pipeline de vendas."""

import pandas as pd


class VendasTransforms:
    """Transformações puras sobre DataFrames de vendas."""

    @staticmethod
    def calcular_valor_total(df_pedidos: pd.DataFrame) -> pd.DataFrame:
        """Cria a coluna VALOR_TOTAL = VALOR_UNITARIO * QUANTIDADE."""
        df = df_pedidos.copy()
        df["VALOR_TOTAL"] = df["VALOR_UNITARIO"] * df["QUANTIDADE"]
        return df

    @staticmethod
    def agregar_por_cliente(df_pedidos: pd.DataFrame) -> pd.DataFrame:
        """Agrupa por ID_CLIENTE e soma o VALOR_TOTAL."""
        df_agregado = df_pedidos.groupby("ID_CLIENTE", as_index=False).agg(
            VALOR_TOTAL_COMPRAS=("VALOR_TOTAL", "sum")
        )
        return df_agregado

    @staticmethod
    def ranking_top_n(df_agregado: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """Ordena por VALOR_TOTAL_COMPRAS (desc) e retorna os top N."""
        df_ranking = (
            df_agregado.sort_values("VALOR_TOTAL_COMPRAS", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )
        return df_ranking

    @staticmethod
    def enriquecer_com_clientes(
        df_ranking: pd.DataFrame, df_clientes: pd.DataFrame
    ) -> pd.DataFrame:
        """Faz join do ranking com os dados de clientes."""
        df_resultado = df_ranking.merge(
            df_clientes[["id", "nome", "email"]],
            left_on="ID_CLIENTE",
            right_on="id",
            how="left",
        )
        df_resultado = df_resultado.drop(columns=["id"])
        df_resultado = df_resultado[
            ["ID_CLIENTE", "nome", "email", "VALOR_TOTAL_COMPRAS"]
        ]
        return df_resultado
