"""Logica pura de transformacao para o pipeline de vendas.

Todas as funcoes recebem e retornam listas de dicionarios,
sem dependencia de qualquer framework externo.
"""


class VendasTransforms:
    """Transformacoes de dados de vendas usando apenas Python puro."""

    @staticmethod
    def calcular_valor_total(pedidos: list[dict]) -> list[dict]:
        """Adiciona o campo VALOR_TOTAL (VALOR_UNITARIO * QUANTIDADE) a cada pedido.

        Args:
            pedidos: Lista de dicts com campos VALOR_UNITARIO e QUANTIDADE.

        Returns:
            Nova lista de dicts com o campo VALOR_TOTAL adicionado.
        """
        resultado: list[dict] = []
        for pedido in pedidos:
            novo = dict(pedido)
            valor_unitario = float(novo["VALOR_UNITARIO"])
            quantidade = int(novo["QUANTIDADE"])
            novo["VALOR_TOTAL"] = round(valor_unitario * quantidade, 2)
            resultado.append(novo)
        return resultado

    @staticmethod
    def agregar_por_cliente(pedidos: list[dict]) -> list[dict]:
        """Agrupa pedidos por ID_CLIENTE e soma o VALOR_TOTAL.

        Args:
            pedidos: Lista de dicts com campos ID_CLIENTE e VALOR_TOTAL.

        Returns:
            Lista de dicts com ID_CLIENTE e VALOR_TOTAL_COMPRAS.
        """
        agregado: dict[str, float] = {}
        for pedido in pedidos:
            cliente_id = str(pedido["ID_CLIENTE"])
            valor = float(pedido["VALOR_TOTAL"])
            agregado[cliente_id] = agregado.get(cliente_id, 0.0) + valor

        return [
            {
                "ID_CLIENTE": cliente_id,
                "VALOR_TOTAL_COMPRAS": round(total, 2),
            }
            for cliente_id, total in agregado.items()
        ]

    @staticmethod
    def top_10_clientes(agregado: list[dict]) -> list[dict]:
        """Retorna os 10 clientes com maior volume de compras.

        Args:
            agregado: Lista de dicts com ID_CLIENTE e VALOR_TOTAL_COMPRAS.

        Returns:
            Lista dos top 10 dicts, ordenados por VALOR_TOTAL_COMPRAS desc.
        """
        ordenado = sorted(
            agregado,
            key=lambda x: float(x["VALOR_TOTAL_COMPRAS"]),
            reverse=True,
        )
        return ordenado[:10]

    @staticmethod
    def enriquecer_com_clientes(top10: list[dict], clientes: list[dict]) -> list[dict]:
        """Enriquece o ranking com dados de clientes (nome, email).

        Args:
            top10: Lista dos top 10 dicts com ID_CLIENTE e VALOR_TOTAL_COMPRAS.
            clientes: Lista de dicts de clientes com id, nome, email.

        Returns:
            Lista enriquecida com NOME e EMAIL do cliente.
        """
        clientes_map: dict[str, dict] = {}
        for cliente in clientes:
            clientes_map[str(cliente["id"])] = cliente

        resultado: list[dict] = []
        for ranking, item in enumerate(top10, start=1):
            cliente_id = str(item["ID_CLIENTE"])
            cliente_info = clientes_map.get(cliente_id, {})
            resultado.append(
                {
                    "RANKING": ranking,
                    "ID_CLIENTE": cliente_id,
                    "NOME": cliente_info.get("nome", "N/A"),
                    "EMAIL": cliente_info.get("email", "N/A"),
                    "VALOR_TOTAL_COMPRAS": item["VALOR_TOTAL_COMPRAS"],
                }
            )
        return resultado
