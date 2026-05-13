from abstract_syntax_tree import Identifier, JoinStatement, LogicalOperator, SelectStatement
from catalog import Catalog
from context import SemanticValidationContext


class SemanticAnalyzer:
    """
    os metodos dessa classe são para checar se todas as tabelas,
    identificadores e colunas existem no catálogo
    """

    def __init__(self, context: SemanticValidationContext | None = None, catalog: Catalog | None = None):
        self.context = context if context is not None else SemanticValidationContext(catalog if catalog is not None else Catalog(), [])

    def analyze(self, tree):
        if isinstance(tree, SelectStatement):
            self._analyze_select_statement(tree)
        elif isinstance(tree, LogicalOperator):
            self._analyze_logical_operator(tree)
        elif isinstance(tree, JoinStatement):
            self._analyze_join_statement(tree)
        else:
            raise ValueError(f"Unsupported statement type: {type(tree)}")

    def _analyze_select_statement(self, statement: SelectStatement):
        if not self.context.catalog.schema.get(statement.table.name):
            raise ValueError(f"Table {statement.table.name} does not exist in the catalog.")
        self.context.push_to_scope(statement.table.name)

        for column in statement.columns:
            parts = column.name.split('.')
            if len(parts) == 2:
                table_name, column_name = parts
                if not self.context.catalog.has_column(table_name, column_name):
                    raise ValueError(f"Column {column_name} does not exist in table {table_name}.")

        if statement.joins:
            for join in statement.joins:
                self._analyze_join_statement(join)

        if statement.where:
            self._analyze_logical_operator(statement.where)

    def _analyze_join_statement(self, join: JoinStatement):
        if not self.context.catalog.schema.get(join.table.name):
            raise ValueError(f"Table {join.table.name} does not exist in the catalog.")
        self.context.push_to_scope(join.table.name)
        self._analyze_logical_operator(join.on)

    def _analyze_logical_operator(self, operator: LogicalOperator):
        if isinstance(operator.left, Identifier):
            if not self._is_valid_identifier(operator.left):
                raise ValueError(f"Invalid identifier: {operator.left.name}")
        elif isinstance(operator.left, LogicalOperator):
            self._analyze_logical_operator(operator.left)

        if isinstance(operator.right, Identifier):
            if not self._is_valid_identifier(operator.right):
                raise ValueError(f"Invalid identifier: {operator.right.name}")
        elif isinstance(operator.right, LogicalOperator):
            self._analyze_logical_operator(operator.right)

    def _is_valid_identifier(self, identifier: Identifier) -> bool:
        parts = identifier.name.split('.')
        if len(parts) == 2:
            table_name, column_name = parts
            for table in self.context.scope:
                if table == table_name and self.context.catalog.has_column(table, column_name):
                    return True
            return False
        return False
