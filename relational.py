from dataclasses import dataclass

from abstract_syntax_tree import LogicalOperator, SelectStatement


class PlanNode:
    def __hash__(self):
        return id(self)

    def __post_init__(cls):
        cls.__hash__ = PlanNode.__hash__

@dataclass
class TableScan(PlanNode):
    table_name: str

    def __hash__(self):
        return hash(id(self))

@dataclass
class Projection(PlanNode):
    child: PlanNode
    columns: list[str]

    def __hash__(self):
        return hash(id(self))

@dataclass
class Selection(PlanNode):
    child: PlanNode
    condition: LogicalOperator

    def __hash__(self):
        return hash(id(self))

@dataclass
class JoinOp(PlanNode):
    left_node: PlanNode
    right_node: PlanNode
    condition: LogicalOperator

    def __hash__(self):
        return hash(id(self))


class ExecutionPlan:
    def build(self, ast_node: SelectStatement) -> PlanNode:
        current_node = TableScan(ast_node.table.name)

        for join_stmt in ast_node.joins:
            right_node = TableScan(table_name=join_stmt.table.name)

            current_node = JoinOp(
                left_node=current_node,
                right_node=right_node,
                condition=join_stmt.on
            )

        if ast_node.where:
            current_node = Selection(child=current_node, condition=ast_node.where)
        col_names = [col.name for col in ast_node.columns]
        return Projection(child=current_node, columns=col_names)

    def execution_order(self, plan: PlanNode) -> list[PlanNode]:
        # pós-ordem: primeiro os filhos, depois o nó atual
        order: list[PlanNode] = []

        def visit(node: PlanNode) -> None:
            if isinstance(node, Projection):
                visit(node.child)
            elif isinstance(node, Selection):
                visit(node.child)
            elif isinstance(node, JoinOp):
                visit(node.left_node)
                visit(node.right_node)
            order.append(node)

        visit(plan)
        return order

    def execution_sequence(self, plan: PlanNode) -> list[tuple[PlanNode, PlanNode | None]]:
        order = self.execution_order(plan)
        sequence: list[tuple[PlanNode, PlanNode | None]] = []
        for index, node in enumerate(order):
            next_node = order[index + 1] if index + 1 < len(order) else None
            sequence.append((node, next_node))
        return sequence
