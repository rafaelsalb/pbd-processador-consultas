import pytest

from abstract_syntax_tree import Identifier, Final, LogicalOperator, SelectStatement, JoinStatement
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from catalog import Catalog


def parse_and_analyze(sql: str, catalog: Catalog | None = None) -> None:
    """Parse SQL and run semantic analysis on the resulting AST."""
    parser = Parser(sql)
    ast = parser.parse()

    analyzer = SemanticAnalyzer(catalog=catalog)
    analyzer.analyze(ast)


def semantic_error(sql: str, catalog: Catalog | None = None) -> None:
    """Verify that semantic analysis fails for the given SQL."""
    with pytest.raises(ValueError):
        parse_and_analyze(sql, catalog)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT idCategoria FROM NonExistentTable;",
        "SELECT idProduto, Nome, Preco FROM InvalidTable;",
        "SELECT idCliente, Nome, Email FROM UnknownTable;",
        "SELECT idPedido, DataPedido, ValorTotalPedido FROM FakeTable;",
    ],
)
def test_semantic_analyzer_rejects_nonexistent_table(sql: str) -> None:
    """Test that semantic analyzer rejects queries referencing non-existent tables."""
    semantic_error(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT Nome FROM Cliente WHERE NonExistentColumn = 10;",
        "SELECT Nome FROM Produto WHERE InvalidPrice > 100;",
        "SELECT Nome FROM Produto WHERE UnknownField < 100;",
        "SELECT Nome FROM Cliente WHERE WrongColumn <> 'X';",
    ],
)
def test_semantic_analyzer_rejects_invalid_column_in_where(sql: str) -> None:
    """Test that semantic analyzer rejects WHERE clauses with invalid columns."""
    semantic_error(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT Nome FROM Cliente WHERE (InvalidColumn = 10);",
        "SELECT Nome FROM Produto WHERE (BadField > 100);",
        "SELECT Nome FROM Produto WHERE (UnknownPrice < 100);",
        "SELECT Nome FROM Cliente WHERE (FakeEmail <> 'X');",
    ],
)
def test_semantic_analyzer_rejects_invalid_column_in_parenthesized_where(sql: str) -> None:
    """Test that semantic analyzer rejects parenthesized WHERE clauses with invalid columns."""
    semantic_error(sql)


def test_semantic_analyzer_rejects_where_with_invalid_table_prefix() -> None:
    """Test that semantic analyzer rejects unqualified column references when only qualified ones exist."""
    semantic_error(
        "SELECT Nome FROM Cliente WHERE InvalidTable.InvalidColumn = 10;"
    )


def test_semantic_analyzer_rejects_join_with_nonexistent_table() -> None:
    """Test that semantic analyzer rejects JOIN with non-existent table."""
    semantic_error(
        "SELECT Cliente.Nome, Pedido.idPedido FROM Cliente "
        "JOIN NonExistentTable ON Cliente.idCliente = NonExistentTable.id;"
    )


def test_semantic_analyzer_rejects_join_with_invalid_column_in_on() -> None:
    """Test that semantic analyzer rejects JOIN with invalid column in ON clause."""
    semantic_error(
        "SELECT Cliente.Nome, Pedido.idPedido FROM Cliente "
        "JOIN Pedido ON Cliente.InvalidColumn = Pedido.Cliente_idCliente;"
    )


def test_semantic_analyzer_rejects_where_with_and_and_invalid_column() -> None:
    """Test that semantic analyzer rejects WHERE with AND when one column is invalid."""
    semantic_error(
        "SELECT Nome FROM Cliente WHERE (InvalidColumn >= 1 AND TipoCliente_idTipoCliente = 2);"
    )
