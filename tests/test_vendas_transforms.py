"""Testes unitários para VendasTransforms."""

import pandas as pd
import pytest

from src.transforms.vendas_transforms import VendasTransforms


@pytest.fixture
def df_pedidos() -> pd.DataFrame:
    """Cria um DataFrame sintético de pedidos."""
    return pd.DataFrame(
        {
            "ID_PEDIDO": ["p1", "p2", "p3", "p4", "p5", "p6"],
            "PRODUTO": [
                "NOTEBOOK",
                "CELULAR",
                "NOTEBOOK",
                "GELADEIRA",
                "CELULAR",
                "TV",
            ],
            "VALOR_UNITARIO": [1500.0, 1000.0, 1500.0, 2000.0, 1000.0, 3000.0],
            "QUANTIDADE": [2, 3, 1, 1, 2, 1],
            "DATA_CRIACAO": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
                "2026-01-05",
                "2026-01-06",
            ],
            "UF": ["SP", "RJ", "SP", "MG", "RJ", "SP"],
            "ID_CLIENTE": [1, 2, 1, 3, 2, 4],
        }
    )


@pytest.fixture
def df_clientes() -> pd.DataFrame:
    """Cria um DataFrame sintético de clientes."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "nome": ["Alice", "Bob", "Carlos", "Diana", "Eva"],
            "email": [
                "alice@test.com",
                "bob@test.com",
                "carlos@test.com",
                "diana@test.com",
                "eva@test.com",
            ],
        }
    )


class TestVendasTransforms:
    """Testes para a classe VendasTransforms."""

    def test_calcular_valor_total(self, df_pedidos: pd.DataFrame) -> None:
        """Testa o cálculo do valor total."""
        resultado = VendasTransforms.calcular_valor_total(df_pedidos)

        assert "VALOR_TOTAL" in resultado.columns
        assert resultado.loc[0, "VALOR_TOTAL"] == 3000.0  # 1500 * 2
        assert resultado.loc[1, "VALOR_TOTAL"] == 3000.0  # 1000 * 3
        assert resultado.loc[2, "VALOR_TOTAL"] == 1500.0  # 1500 * 1
        assert resultado.loc[3, "VALOR_TOTAL"] == 2000.0  # 2000 * 1
        assert resultado.loc[4, "VALOR_TOTAL"] == 2000.0  # 1000 * 2
        assert resultado.loc[5, "VALOR_TOTAL"] == 3000.0  # 3000 * 1

    def test_calcular_valor_total_nao_modifica_original(
        self, df_pedidos: pd.DataFrame
    ) -> None:
        """Garante que a função é pura e não modifica o DataFrame original."""
        colunas_originais = list(df_pedidos.columns)
        VendasTransforms.calcular_valor_total(df_pedidos)
        assert list(df_pedidos.columns) == colunas_originais

    def test_agregar_por_cliente(self, df_pedidos: pd.DataFrame) -> None:
        """Testa a agregação por cliente."""
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        resultado = VendasTransforms.agregar_por_cliente(df_com_total)

        assert "ID_CLIENTE" in resultado.columns
        assert "VALOR_TOTAL_COMPRAS" in resultado.columns
        assert len(resultado) == 4  # 4 clientes distintos

        cliente_1 = resultado[resultado["ID_CLIENTE"] == 1]
        assert cliente_1["VALOR_TOTAL_COMPRAS"].values[0] == 4500.0  # 3000 + 1500

        cliente_2 = resultado[resultado["ID_CLIENTE"] == 2]
        assert cliente_2["VALOR_TOTAL_COMPRAS"].values[0] == 5000.0  # 3000 + 2000

    def test_ranking_top_n(self, df_pedidos: pd.DataFrame) -> None:
        """Testa o ranking Top N."""
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.ranking_top_n(df_agregado, n=2)

        assert len(resultado) == 2
        # O primeiro deve ser o cliente com maior valor
        assert (
            resultado.iloc[0]["VALOR_TOTAL_COMPRAS"]
            >= resultado.iloc[1]["VALOR_TOTAL_COMPRAS"]
        )

    def test_ranking_top_n_com_n_maior_que_registros(
        self, df_pedidos: pd.DataFrame
    ) -> None:
        """Testa ranking quando N é maior que o número de clientes."""
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.ranking_top_n(df_agregado, n=100)

        assert len(resultado) == 4  # Retorna todos os 4 clientes

    def test_enriquecer_com_clientes(
        self, df_pedidos: pd.DataFrame, df_clientes: pd.DataFrame
    ) -> None:
        """Testa o enriquecimento com dados de clientes."""
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        df_ranking = VendasTransforms.ranking_top_n(df_agregado, n=10)
        resultado = VendasTransforms.enriquecer_com_clientes(df_ranking, df_clientes)

        assert "nome" in resultado.columns
        assert "email" in resultado.columns
        assert "ID_CLIENTE" in resultado.columns
        assert "VALOR_TOTAL_COMPRAS" in resultado.columns
        assert "id" not in resultado.columns  # Coluna duplicada removida

    def test_pipeline_completo(
        self, df_pedidos: pd.DataFrame, df_clientes: pd.DataFrame
    ) -> None:
        """Testa o fluxo completo de transformações."""
        transforms = VendasTransforms()

        df_com_total = transforms.calcular_valor_total(df_pedidos)
        df_agregado = transforms.agregar_por_cliente(df_com_total)
        df_ranking = transforms.ranking_top_n(df_agregado, n=2)
        df_resultado = transforms.enriquecer_com_clientes(df_ranking, df_clientes)

        assert len(df_resultado) == 2
        assert (
            df_resultado.iloc[0]["VALOR_TOTAL_COMPRAS"]
            >= df_resultado.iloc[1]["VALOR_TOTAL_COMPRAS"]
        )
        assert all(
            col in df_resultado.columns
            for col in ["ID_CLIENTE", "nome", "email", "VALOR_TOTAL_COMPRAS"]
        )
