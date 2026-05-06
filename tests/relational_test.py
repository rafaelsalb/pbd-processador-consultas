from abstract_syntax_tree import Final, Identifier, LogicalOperator
from parser import Parser
from relational import ExecutionPlan, JoinOp, Projection, Selection, TableScan


def build_plan(sql: str):
    parser = Parser(sql)
    ast = parser.parse()
    return ExecutionPlan().build(ast)


def test_execution_plan_basic_select() -> None:
    plan = build_plan("SELECT idCategoria FROM Categoria;")

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, TableScan)
    assert plan.child.table_name == "Categoria"
    assert plan.columns == ["idCategoria"]


def test_execution_plan_select_with_where() -> None:
    plan = build_plan("SELECT Nome FROM Cliente WHERE idCliente = 10;")

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, Selection)
    assert isinstance(plan.child.child, TableScan)
    assert plan.child.child.table_name == "Cliente"

    expected_condition = LogicalOperator(
        left=Identifier(name="idCliente"),
        operator="=",
        right=Final(value=10),
    )
    assert plan.child.condition == expected_condition
    assert plan.columns == ["Nome"]


def test_execution_plan_select_with_join() -> None:
    plan = build_plan(
        "SELECT Cliente.Nome, Pedido.idPedido FROM Cliente "
        "JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente;"
    )

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, JoinOp)
    assert isinstance(plan.child.left_node, TableScan)
    assert isinstance(plan.child.right_node, TableScan)

    assert plan.child.left_node.table_name == "Cliente"
    assert plan.child.right_node.table_name == "Pedido"

    expected_condition = LogicalOperator(
        left=Identifier(name="Cliente.idCliente"),
        operator="=",
        right=Identifier(name="Pedido.Cliente_idCliente"),
    )
    assert plan.child.condition == expected_condition
    assert plan.columns == ["Cliente.Nome", "Pedido.idPedido"]


def test_execution_plan_join_then_where() -> None:
    plan = build_plan(
        "SELECT Cliente.Nome, Pedido.idPedido FROM Cliente "
        "JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente "
        "WHERE Pedido.idPedido = 1001;"
    )

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, Selection)
    assert isinstance(plan.child.child, JoinOp)

    expected_where = LogicalOperator(
        left=Identifier(name="Pedido.idPedido"),
        operator="=",
        right=Final(value=1001),
    )
    assert plan.child.condition == expected_where


def test_execution_plan_multiple_joins() -> None:
    plan = build_plan(
        "SELECT Cliente.Nome, Pedido.idPedido, Status.Descricao FROM Cliente "
        "JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente "
        "JOIN Status ON Pedido.Status_idStatus = Status.idStatus;"
    )

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, JoinOp)
    assert isinstance(plan.child.left_node, JoinOp)
    assert isinstance(plan.child.right_node, TableScan)

    assert plan.child.left_node.left_node.table_name == "Cliente"
    assert plan.child.left_node.right_node.table_name == "Pedido"
    assert plan.child.right_node.table_name == "Status"

    expected_first_join = LogicalOperator(
        left=Identifier(name="Cliente.idCliente"),
        operator="=",
        right=Identifier(name="Pedido.Cliente_idCliente"),
    )
    expected_second_join = LogicalOperator(
        left=Identifier(name="Pedido.Status_idStatus"),
        operator="=",
        right=Identifier(name="Status.idStatus"),
    )
    assert plan.child.left_node.condition == expected_first_join
    assert plan.child.condition == expected_second_join
    assert plan.columns == ["Cliente.Nome", "Pedido.idPedido", "Status.Descricao"]


def test_execution_plan_where_with_and_conditions() -> None:
    plan = build_plan(
        "SELECT Nome FROM Cliente "
        "WHERE idCliente >= 1 AND TipoCliente_idTipoCliente = 2;"
    )

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, Selection)

    expected_left = LogicalOperator(
        left=Identifier(name="idCliente"),
        operator=">=",
        right=Final(value=1),
    )
    expected_condition = LogicalOperator(
        left=expected_left,
        operator="AND",
        right=LogicalOperator(
            left=Identifier(name="TipoCliente_idTipoCliente"),
            operator="=",
            right=Final(value=2),
        ),
    )
    assert plan.child.condition == expected_condition


def test_execution_plan_where_with_parentheses_and_and() -> None:
    plan = build_plan(
        "SELECT Nome FROM Cliente "
        "WHERE (idCliente >= 1 AND TipoCliente_idTipoCliente = 2);"
    )

    assert isinstance(plan, Projection)
    assert isinstance(plan.child, Selection)

    expected_left = LogicalOperator(
        left=Identifier(name="idCliente"),
        operator=">=",
        right=Final(value=1),
    )
    expected_condition = LogicalOperator(
        left=expected_left,
        operator="AND",
        right=LogicalOperator(
            left=Identifier(name="TipoCliente_idTipoCliente"),
            operator="=",
            right=Final(value=2),
        ),
    )
    assert plan.child.condition == expected_condition
