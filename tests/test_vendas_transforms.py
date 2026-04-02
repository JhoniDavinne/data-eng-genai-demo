"""Testes unitarios para as transformacoes de vendas."""

import pytest

from src.transforms.vendas_transforms import VendasTransforms


@pytest.fixture
def transforms():
    """Fixture que retorna uma instancia de VendasTransforms."""
    return VendasTransforms()


@pytest.fixture
def pedidos_sample():
    """Dados sinteticos de pedidos."""
    return [
        {
            "ID_PEDIDO": "aaa-111",
            "PRODUTO": "NOTEBOOK",
            "VALOR_UNITARIO": "1500.0",
            "QUANTIDADE": "2",
            "DATA_CRIACAO": "2026-01-01T10:00:00",
            "UF": "SP",
            "ID_CLIENTE": "1",
        },
        {
            "ID_PEDIDO": "bbb-222",
            "PRODUTO": "CELULAR",
            "VALOR_UNITARIO": "1000.0",
            "QUANTIDADE": "3",
            "DATA_CRIACAO": "2026-01-02T11:00:00",
            "UF": "RJ",
            "ID_CLIENTE": "2",
        },
        {
            "ID_PEDIDO": "ccc-333",
            "PRODUTO": "GELADEIRA",
            "VALOR_UNITARIO": "2000.0",
            "QUANTIDADE": "1",
            "DATA_CRIACAO": "2026-01-03T12:00:00",
            "UF": "MG",
            "ID_CLIENTE": "1",
        },
        {
            "ID_PEDIDO": "ddd-444",
            "PRODUTO": "TELEVISAO",
            "VALOR_UNITARIO": "3000.0",
            "QUANTIDADE": "1",
            "DATA_CRIACAO": "2026-01-04T13:00:00",
            "UF": "BA",
            "ID_CLIENTE": "3",
        },
    ]


@pytest.fixture
def clientes_sample():
    """Dados sinteticos de clientes."""
    return [
        {
            "id": 1,
            "nome": "Alice Silva",
            "data_nasc": "1990-01-01",
            "cpf": "111.111.111-11",
            "email": "alice@email.com",
            "interesses": ["Tecnologia"],
            "carteira_investimentos": {},
        },
        {
            "id": 2,
            "nome": "Bob Santos",
            "data_nasc": "1985-05-15",
            "cpf": "222.222.222-22",
            "email": "bob@email.com",
            "interesses": ["Esportes"],
            "carteira_investimentos": {},
        },
        {
            "id": 3,
            "nome": "Carlos Oliveira",
            "data_nasc": "2000-12-25",
            "cpf": "333.333.333-33",
            "email": "carlos@email.com",
            "interesses": ["Musica"],
            "carteira_investimentos": {},
        },
    ]


class TestCalcularValorTotal:
    """Testes para calcular_valor_total."""

    def test_calcula_valor_total_corretamente(self, transforms, pedidos_sample):
        resultado = transforms.calcular_valor_total(pedidos_sample)

        assert len(resultado) == 4
        assert resultado[0]["VALOR_TOTAL"] == 3000.0  # 1500 * 2
        assert resultado[1]["VALOR_TOTAL"] == 3000.0  # 1000 * 3
        assert resultado[2]["VALOR_TOTAL"] == 2000.0  # 2000 * 1
        assert resultado[3]["VALOR_TOTAL"] == 3000.0  # 3000 * 1

    def test_preserva_campos_originais(self, transforms, pedidos_sample):
        resultado = transforms.calcular_valor_total(pedidos_sample)

        assert resultado[0]["PRODUTO"] == "NOTEBOOK"
        assert resultado[0]["ID_CLIENTE"] == "1"

    def test_nao_modifica_lista_original(self, transforms, pedidos_sample):
        original_len = len(pedidos_sample)
        transforms.calcular_valor_total(pedidos_sample)

        assert len(pedidos_sample) == original_len
        assert "VALOR_TOTAL" not in pedidos_sample[0]

    def test_lista_vazia(self, transforms):
        resultado = transforms.calcular_valor_total([])
        assert resultado == []


class TestAgregarPorCliente:
    """Testes para agregar_por_cliente."""

    def test_agrega_corretamente(self, transforms):
        pedidos = [
            {"ID_CLIENTE": "1", "VALOR_TOTAL": 3000.0},
            {"ID_CLIENTE": "2", "VALOR_TOTAL": 3000.0},
            {"ID_CLIENTE": "1", "VALOR_TOTAL": 2000.0},
            {"ID_CLIENTE": "3", "VALOR_TOTAL": 3000.0},
        ]
        resultado = transforms.agregar_por_cliente(pedidos)

        resultado_map = {r["ID_CLIENTE"]: r for r in resultado}
        assert len(resultado) == 3
        assert resultado_map["1"]["VALOR_TOTAL_COMPRAS"] == 5000.0
        assert resultado_map["2"]["VALOR_TOTAL_COMPRAS"] == 3000.0
        assert resultado_map["3"]["VALOR_TOTAL_COMPRAS"] == 3000.0

    def test_cliente_unico(self, transforms):
        pedidos = [{"ID_CLIENTE": "10", "VALOR_TOTAL": 500.0}]
        resultado = transforms.agregar_por_cliente(pedidos)

        assert len(resultado) == 1
        assert resultado[0]["VALOR_TOTAL_COMPRAS"] == 500.0

    def test_lista_vazia(self, transforms):
        resultado = transforms.agregar_por_cliente([])
        assert resultado == []


class TestTop10Clientes:
    """Testes para top_10_clientes."""

    def test_retorna_top_10(self, transforms):
        dados = [
            {"ID_CLIENTE": str(i), "VALOR_TOTAL_COMPRAS": float(i * 100)}
            for i in range(1, 16)
        ]
        resultado = transforms.top_10_clientes(dados)

        assert len(resultado) == 10
        assert resultado[0]["VALOR_TOTAL_COMPRAS"] == 1500.0
        assert resultado[9]["VALOR_TOTAL_COMPRAS"] == 600.0

    def test_menos_de_10_clientes(self, transforms):
        dados = [
            {"ID_CLIENTE": "1", "VALOR_TOTAL_COMPRAS": 1000.0},
            {"ID_CLIENTE": "2", "VALOR_TOTAL_COMPRAS": 2000.0},
        ]
        resultado = transforms.top_10_clientes(dados)

        assert len(resultado) == 2
        assert resultado[0]["VALOR_TOTAL_COMPRAS"] == 2000.0

    def test_ordenacao_decrescente(self, transforms):
        dados = [
            {"ID_CLIENTE": "1", "VALOR_TOTAL_COMPRAS": 100.0},
            {"ID_CLIENTE": "2", "VALOR_TOTAL_COMPRAS": 300.0},
            {"ID_CLIENTE": "3", "VALOR_TOTAL_COMPRAS": 200.0},
        ]
        resultado = transforms.top_10_clientes(dados)

        valores = [r["VALOR_TOTAL_COMPRAS"] for r in resultado]
        assert valores == [300.0, 200.0, 100.0]

    def test_lista_vazia(self, transforms):
        resultado = transforms.top_10_clientes([])
        assert resultado == []


class TestEnriquecerComClientes:
    """Testes para enriquecer_com_clientes."""

    def test_enriquece_corretamente(self, transforms, clientes_sample):
        top10 = [
            {"ID_CLIENTE": "1", "VALOR_TOTAL_COMPRAS": 5000.0},
            {"ID_CLIENTE": "2", "VALOR_TOTAL_COMPRAS": 3000.0},
        ]
        resultado = transforms.enriquecer_com_clientes(top10, clientes_sample)

        assert len(resultado) == 2
        assert resultado[0]["RANKING"] == 1
        assert resultado[0]["NOME"] == "Alice Silva"
        assert resultado[0]["EMAIL"] == "alice@email.com"
        assert resultado[0]["VALOR_TOTAL_COMPRAS"] == 5000.0
        assert resultado[1]["RANKING"] == 2
        assert resultado[1]["NOME"] == "Bob Santos"

    def test_cliente_nao_encontrado(self, transforms):
        top10 = [
            {"ID_CLIENTE": "999", "VALOR_TOTAL_COMPRAS": 1000.0},
        ]
        resultado = transforms.enriquecer_com_clientes(top10, [])

        assert resultado[0]["NOME"] == "N/A"
        assert resultado[0]["EMAIL"] == "N/A"

    def test_ranking_sequencial(self, transforms, clientes_sample):
        top10 = [
            {"ID_CLIENTE": str(i), "VALOR_TOTAL_COMPRAS": float(i * 100)}
            for i in range(1, 4)
        ]
        resultado = transforms.enriquecer_com_clientes(top10, clientes_sample)

        rankings = [r["RANKING"] for r in resultado]
        assert rankings == [1, 2, 3]
