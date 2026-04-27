import pytest

from parser import Parser


def parse_ok(sql: str) -> None:
    parser = Parser(sql)
    parser.parse()

    # Garante que a query inteira foi reconhecida pelo parser.
    # Enquanto WHERE/JOIN/ON não estiverem implementados, esses casos falham aqui.
    assert parser.syntactic_analyzer is not None
    assert parser.syntactic_analyzer.is_at_end(), (
        f"Parser não consumiu todos os tokens da query. Parou em {parser.syntactic_analyzer._peek()}: {sql}"
    )


def parse_error(sql: str) -> None:
    with pytest.raises((SyntaxError, RuntimeError)):
        Parser(sql).parse()


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT idCategoria FROM Categoria",
        "SELECT idProduto, Nome, Preco FROM Produto",
        "SELECT idCliente, Nome, Email FROM Cliente",
        "SELECT idPedido, DataPedido, ValorTotalPedido FROM Pedido",
    ],
)
def test_parser_accepts_basic_select_from(sql: str) -> None:
    parse_ok(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "FROM Categoria SELECT idCategoria",
        "SELECT FROM Categoria",
        "SELECT idCategoria, FROM Categoria",
        "SELECT idCategoria FROM Categoria @",
    ],
)
def test_parser_rejects_invalid_basic_structure(sql: str) -> None:
    parse_error(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT Nome FROM Cliente WHERE idCliente = 10",
        "SELECT Nome FROM Produto WHERE Preco > 100",
        "SELECT Nome FROM Produto WHERE Preco < 100",
        "SELECT Nome FROM Produto WHERE Preco <= 100",
        "SELECT Nome FROM Produto WHERE Preco >= 100",
        "SELECT Nome FROM Cliente WHERE Email <> 'X'",
    ],
)
def test_parser_should_accept_where_with_comparison_operators(sql: str) -> None:
    parse_ok(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT Nome FROM Cliente WHERE (idCliente = 10)",
        "SELECT Nome FROM Produto WHERE (Preco > 100)",
        "SELECT Nome FROM Produto WHERE (Preco < 100)",
        "SELECT Nome FROM Produto WHERE (Preco <= 100)",
        "SELECT Nome FROM Produto WHERE (Preco >= 100)",
        "SELECT Nome FROM Cliente WHERE (Email <> 'X')",
    ],
)
def test_parser_should_accept_where_with_parentheses(sql: str) -> None:
    parse_ok(sql)


def test_parser_should_accept_where_with_and_and_parentheses() -> None:
    parse_ok(
        "SELECT Nome FROM Cliente WHERE (idCliente >= 1 AND TipoCliente_idTipoCliente = 2)"
        # "SELECT Nome FROM Cliente WHERE idCliente >= 1 AND TipoCliente_idTipoCliente = 2"
    )


def test_parser_should_accept_join_on() -> None:
    parse_ok(
        "SELECT Cliente.Nome, Pedido.idPedido FROM Cliente "
        "JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente"
    )


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT Nome FROM Cliente WHERE (idCliente = 10",
        "SELECT Nome FROM Produto WHERE Preco > 100)",
        "SELECT Nome FROM Produto WHERE (Preco <= )",
        "SELECT Nome FROM Cliente WHERE ()",
        "SELECT Cliente.Nome FROM Cliente JOIN Pedido ON (Cliente.idCliente = Pedido.Cliente_idCliente",
    ],
)
def test_parser_should_reject_invalid_parentheses(sql: str) -> None:
    parse_error(sql)
