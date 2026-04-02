import pytest
from pyspark.sql import SparkSession

from src.transforms.vendas_transforms import VendasTransforms


@pytest.fixture(scope="session")
def spark():
    """Cria uma SparkSession para os testes."""
    session = (
        SparkSession.builder.master("local[1]")
        .appName("TestVendasTransforms")
        .getOrCreate()
    )
    yield session
    session.stop()


@pytest.fixture
def df_pedidos(spark):
    """Cria um DataFrame sintético de pedidos."""
    dados = [
        ("ped-1", "NOTEBOOK", 1500.0, 2, "2026-01-01T10:00:00", "SP", 1),
        ("ped-2", "CELULAR", 1000.0, 3, "2026-01-02T11:00:00", "RJ", 2),
        ("ped-3", "GELADEIRA", 2000.0, 1, "2026-01-03T12:00:00", "MG", 1),
        ("ped-4", "TV", 2500.0, 1, "2026-01-04T13:00:00", "SP", 3),
        ("ped-5", "FONE", 200.0, 5, "2026-01-05T14:00:00", "RJ", 2),
        ("ped-6", "TABLET", 800.0, 2, "2026-01-06T15:00:00", "BA", 4),
        ("ped-7", "MOUSE", 50.0, 10, "2026-01-07T16:00:00", "SP", 5),
        ("ped-8", "TECLADO", 150.0, 3, "2026-01-08T17:00:00", "RJ", 6),
        ("ped-9", "MONITOR", 1200.0, 2, "2026-01-09T18:00:00", "MG", 7),
        ("ped-10", "IMPRESSORA", 600.0, 1, "2026-01-10T19:00:00", "SP", 8),
        ("ped-11", "WEBCAM", 300.0, 2, "2026-01-11T20:00:00", "RJ", 9),
        ("ped-12", "HD", 400.0, 3, "2026-01-12T21:00:00", "BA", 10),
        ("ped-13", "SSD", 500.0, 2, "2026-01-13T22:00:00", "SP", 11),
    ]
    colunas = [
        "ID_PEDIDO",
        "PRODUTO",
        "VALOR_UNITARIO",
        "QUANTIDADE",
        "DATA_CRIACAO",
        "UF",
        "ID_CLIENTE",
    ]
    return spark.createDataFrame(dados, colunas)


@pytest.fixture
def df_clientes(spark):
    """Cria um DataFrame sintético de clientes."""
    dados = [
        (1, "Ana Silva", "ana@email.com"),
        (2, "Bruno Costa", "bruno@email.com"),
        (3, "Carla Souza", "carla@email.com"),
        (4, "Daniel Lima", "daniel@email.com"),
        (5, "Elena Rocha", "elena@email.com"),
        (6, "Felipe Dias", "felipe@email.com"),
        (7, "Gabi Melo", "gabi@email.com"),
        (8, "Hugo Reis", "hugo@email.com"),
        (9, "Iris Nunes", "iris@email.com"),
        (10, "João Alves", "joao@email.com"),
        (11, "Karen Luz", "karen@email.com"),
    ]
    colunas = ["id", "nome", "email"]
    return spark.createDataFrame(dados, colunas)


class TestCalcularValorTotal:
    def test_coluna_valor_total_criada(self, df_pedidos):
        resultado = VendasTransforms.calcular_valor_total(df_pedidos)
        assert "VALOR_TOTAL" in resultado.columns

    def test_valor_total_correto(self, spark, df_pedidos):
        resultado = VendasTransforms.calcular_valor_total(df_pedidos)
        linha = resultado.filter(resultado.ID_PEDIDO == "ped-1").first()
        assert linha is not None
        assert linha["VALOR_TOTAL"] == 3000.0  # 1500 * 2

    def test_valor_total_multiplicacao(self, spark, df_pedidos):
        resultado = VendasTransforms.calcular_valor_total(df_pedidos)
        linha = resultado.filter(resultado.ID_PEDIDO == "ped-2").first()
        assert linha is not None
        assert linha["VALOR_TOTAL"] == 3000.0  # 1000 * 3


class TestAgregarPorCliente:
    def test_agrupamento_por_cliente(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        resultado = VendasTransforms.agregar_por_cliente(df_com_total)
        # Cliente 1 tem 2 pedidos
        linha = resultado.filter(resultado.ID_CLIENTE == 1).first()
        assert linha is not None
        assert linha["QTD_PEDIDOS"] == 2
        assert linha["TOTAL_COMPRAS"] == 5000.0  # 3000 + 2000

    def test_colunas_resultado(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        resultado = VendasTransforms.agregar_por_cliente(df_com_total)
        assert "ID_CLIENTE" in resultado.columns
        assert "TOTAL_COMPRAS" in resultado.columns
        assert "QTD_PEDIDOS" in resultado.columns


class TestRankearTopN:
    def test_top_3(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.rankear_top_n(df_agregado, n=3)
        assert resultado.count() == 3

    def test_ordem_ranking(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.rankear_top_n(df_agregado, n=3)
        linhas = resultado.collect()
        assert linhas[0]["RANKING"] == 1
        assert linhas[1]["RANKING"] == 2
        assert linhas[2]["RANKING"] == 3
        # O primeiro deve ter maior TOTAL_COMPRAS
        assert linhas[0]["TOTAL_COMPRAS"] >= linhas[1]["TOTAL_COMPRAS"]

    def test_top_10_default(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.rankear_top_n(df_agregado)
        assert resultado.count() == 10  # Padrão é top 10


class TestEnriquecerComClientes:
    def test_join_com_clientes(self, df_pedidos, df_clientes):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        df_top = VendasTransforms.rankear_top_n(df_agregado, n=3)
        resultado = VendasTransforms.enriquecer_com_clientes(df_top, df_clientes)
        assert "nome" in resultado.columns
        assert "email" in resultado.columns
        assert resultado.count() == 3
