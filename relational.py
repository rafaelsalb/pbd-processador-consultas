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
