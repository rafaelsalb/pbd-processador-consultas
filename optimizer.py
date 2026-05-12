from abstract_syntax_tree import Identifier, LogicalOperator
from relational import JoinOp, PlanNode, Projection, Selection, TableScan


class SelectionRule:
    @staticmethod
    def _tables_from_identifier(identifier: Identifier) -> set:
        parts = identifier.name.split(".")
        if len(parts) == 2:
            return {parts[0]}
        return set()

    @staticmethod
    def _tables_in_condition(condition) -> set:
        tables = set()
        if isinstance(condition, LogicalOperator):
            tables.update(SelectionRule._tables_in_condition(condition.left))
            tables.update(SelectionRule._tables_in_condition(condition.right))
        elif isinstance(condition, Identifier):
            tables.update(SelectionRule._tables_from_identifier(condition))
        return tables

    @staticmethod
    def _tables_in_plan(plan_node) -> set:
        tables = set()
        if isinstance(plan_node, TableScan):
            tables.add(plan_node.table_name)
        if hasattr(plan_node, "child"):
            tables.update(SelectionRule._tables_in_plan(plan_node.child))
        if hasattr(plan_node, "left_node"):
            tables.update(SelectionRule._tables_in_plan(plan_node.left_node))
        if hasattr(plan_node, "right_node"):
            tables.update(SelectionRule._tables_in_plan(plan_node.right_node))
        return tables

    @staticmethod
    def _split_conjuncts(condition) -> list:
        if isinstance(condition, LogicalOperator) and condition.operator == "AND":
            return SelectionRule._split_conjuncts(condition.left) + SelectionRule._split_conjuncts(condition.right)
        return [condition]

    @staticmethod
    def _combine_conjuncts(conjuncts: list) -> LogicalOperator | None:
        if not conjuncts:
            return None
        current = conjuncts[0]
        for next_condition in conjuncts[1:]:
            current = LogicalOperator(
                left=current,
                operator="AND",
                right=next_condition,
            )
        return current

    @staticmethod
    def apply(node: Selection) -> PlanNode:
        if not isinstance(node.child, JoinOp):
            return node

        join_node = node.child
        left_tables = SelectionRule._tables_in_plan(join_node.left_node)
        right_tables = SelectionRule._tables_in_plan(join_node.right_node)

        left_conditions: list = []
        right_conditions: list = []
        remaining_conditions: list = []

        for predicate in SelectionRule._split_conjuncts(node.condition):
            predicate_tables = SelectionRule._tables_in_condition(predicate)

            if predicate_tables and predicate_tables.issubset(left_tables):
                left_conditions.append(predicate)
            elif predicate_tables and predicate_tables.issubset(right_tables):
                right_conditions.append(predicate)
            else:
                remaining_conditions.append(predicate)

        if left_conditions:
            join_node.left_node = Selection(
                child=join_node.left_node,
                condition=SelectionRule._combine_conjuncts(left_conditions),
            )

        if right_conditions:
            join_node.right_node = Selection(
                child=join_node.right_node,
                condition=SelectionRule._combine_conjuncts(right_conditions),
            )

        remaining = SelectionRule._combine_conjuncts(remaining_conditions)
        if remaining is None:
            return join_node

        node.child = join_node
        node.condition = remaining
        return node


class ProjectionRule:
    @staticmethod
    def _columns_from_identifier(identifier: Identifier) -> set:
        return {identifier.name}

    @staticmethod
    def _columns_in_condition(condition) -> set:
        columns = set()
        if isinstance(condition, LogicalOperator):
            columns.update(ProjectionRule._columns_in_condition(condition.left))
            columns.update(ProjectionRule._columns_in_condition(condition.right))
        elif isinstance(condition, Identifier):
            columns.update(ProjectionRule._columns_from_identifier(condition))
        return columns

    @staticmethod
    def _tables_in_plan(plan_node) -> set:
        tables = set()
        if isinstance(plan_node, TableScan):
            tables.add(plan_node.table_name)
        if hasattr(plan_node, "child"):
            tables.update(ProjectionRule._tables_in_plan(plan_node.child))
        if hasattr(plan_node, "left_node"):
            tables.update(ProjectionRule._tables_in_plan(plan_node.left_node))
        if hasattr(plan_node, "right_node"):
            tables.update(ProjectionRule._tables_in_plan(plan_node.right_node))
        return tables

    @staticmethod
    def _merge_columns(primary: list, extra: set | list) -> list:
        merged = []
        seen = set()
        for col in primary:
            if col not in seen:
                merged.append(col)
                seen.add(col)
        for col in extra:
            if col not in seen:
                merged.append(col)
                seen.add(col)
        return merged

    @staticmethod
    def _filter_columns_by_tables(columns: list, tables: set) -> list:
        filtered = []
        for col in columns:
            parts = col.split(".")
            if len(parts) == 2 and parts[0] in tables:
                filtered.append(col)
        return filtered

    @staticmethod
    def _ensure_projection(node: PlanNode, required_columns: list) -> PlanNode:
        if not required_columns:
            return node
        if isinstance(node, Projection):
            required_set = set(required_columns)
            new_columns = [col for col in node.columns if col in required_set]
            if not new_columns:
                new_columns = node.columns
            node.columns = new_columns
            node.child = ProjectionRule._push_projection(node.child, new_columns)
            return node
        projection = Projection(child=node, columns=required_columns)
        projection.child = ProjectionRule._push_projection(projection.child, required_columns)
        return projection

    @staticmethod
    def _push_projection(node: PlanNode, required_columns: list) -> PlanNode:
        if isinstance(node, Projection):
            required_set = set(required_columns)
            new_columns = [col for col in node.columns if col in required_set]
            if not new_columns:
                new_columns = node.columns
            node.columns = new_columns
            node.child = ProjectionRule._push_projection(node.child, new_columns)
            return node

        if isinstance(node, Selection):
            condition_columns = ProjectionRule._columns_in_condition(node.condition)
            needed = ProjectionRule._merge_columns(required_columns, condition_columns)
            node.child = ProjectionRule._push_projection(node.child, needed)
            return node

        if isinstance(node, JoinOp):
            left_tables = ProjectionRule._tables_in_plan(node.left_node)
            right_tables = ProjectionRule._tables_in_plan(node.right_node)

            join_columns = ProjectionRule._columns_in_condition(node.condition)
            left_needed = ProjectionRule._merge_columns(
                ProjectionRule._filter_columns_by_tables(required_columns, left_tables),
                ProjectionRule._filter_columns_by_tables(list(join_columns), left_tables),
            )
            right_needed = ProjectionRule._merge_columns(
                ProjectionRule._filter_columns_by_tables(required_columns, right_tables),
                ProjectionRule._filter_columns_by_tables(list(join_columns), right_tables),
            )

            node.left_node = ProjectionRule._ensure_projection(node.left_node, left_needed)
            node.right_node = ProjectionRule._ensure_projection(node.right_node, right_needed)
            return node

        if isinstance(node, TableScan):
            return node

        return node

    @staticmethod
    def apply(node: Projection) -> PlanNode:
        node.child = ProjectionRule._push_projection(node.child, node.columns)
        return node


class TreeOptimizer:
    def optimize(self, node: PlanNode) -> PlanNode:
        """
        Recursively walks the execution graph and applies optimization rules.
        """
        if isinstance(node, Selection):
            optimized = SelectionRule.apply(node)
            if isinstance(optimized, Selection):
                optimized.child = self.optimize(optimized.child)
                return optimized
            if isinstance(optimized, JoinOp):
                optimized.left_node = self.optimize(optimized.left_node)
                optimized.right_node = self.optimize(optimized.right_node)
                return optimized
            return optimized

        if isinstance(node, Projection):
            optimized = ProjectionRule.apply(node)
            optimized.child = self.optimize(optimized.child)
            return optimized

        if isinstance(node, JoinOp):
            node.left_node = self.optimize(node.left_node)
            node.right_node = self.optimize(node.right_node)
            return node

        return node
