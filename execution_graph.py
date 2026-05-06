import pprint

from abstract_syntax_tree import Final, Identifier, LogicalOperator
from relational import ExecutionPlan, JoinOp, Projection, Selection
import matplotlib.pyplot as plt
import networkx as nx

from tree_traversal import breadth_first_traversal



class ExecutionGraph:
    # def __init__(self, graph: nx.DiGraph):
    #     self.graph = graph

    # @classmethod
    # def from_plan(cls, plan: ExecutionPlan):
    #     graph = nx.DiGraph()
    #     graph.add_node(plan)

    #     def add_edges(node):
    #         if isinstance(node, Projection):
    #             graph.add_edge(node, node.child)
    #             add_edges(node.child)
    #         elif isinstance(node, Selection):
    #             graph.add_edge(node, node.child)
    #             add_edges(node.child)
    #         elif isinstance(node, JoinOp):
    #             graph.add_edge(node, node.left_node)
    #             graph.add_edge(node, node.right_node)
    #             add_edges(node.left_node)
    #             add_edges(node.right_node)

    #     add_edges(plan)
    #     return cls(graph=graph)

    def _print_step(self, node, indent=0):
        prefix = " " * indent * 4
        if isinstance(node, Projection):
            print(f"{prefix}Projection: columns={node.columns}")
            self._print_step(node.child, indent + 2)
        elif isinstance(node, Selection):
            print(f"{prefix}Selection: condition={node.condition}")
            self._print_step(node.child, indent + 2)
        elif isinstance(node, JoinOp):
            print(f"{prefix}Join: condition={node.condition}")
            self._print_step(node.left_node, indent + 2)
            self._print_step(node.right_node, indent + 2)
        else:
            print(f"{prefix}TableScan: table={node.table_name}")

    def _node_label(self, node):
        if isinstance(node, Projection):
            columns = pprint.pformat(node.columns, indent=4)
            return f"Projection:\ncolumns={columns}"
        if isinstance(node, Selection):
            condition = pprint.pformat(node.condition, indent=4)
            return f"Selection:\ncondition={condition}"
        if isinstance(node, JoinOp):
            condition = pprint.pformat(node.condition, indent=4)
            return f"Join:\ncondition={condition}"
        return f"TableScan:\ntable={node.table_name}"

    def visualize(self, plan: ExecutionPlan):
        graph = nx.DiGraph()
        for node in breadth_first_traversal(plan):
            graph.add_node(node)
            if isinstance(node, Projection):
                graph.add_edge(node, node.child)
            elif isinstance(node, Selection):
                graph.add_edge(node, node.child)
            elif isinstance(node, JoinOp):
                graph.add_edge(node, node.left_node)
                graph.add_edge(node, node.right_node)
        pos = nx.spring_layout(graph)
        labels = {node: self._node_label(node) for node in graph.nodes()}
        nx.draw(graph, pos, with_labels=True, labels=labels)

        plt.show()
        # for node in plan:
        # self._print_step(plan)

    def jsonify(self, plan: ExecutionPlan):
        def logical_to_dict(operator):
            if isinstance(operator, LogicalOperator):
                return {
                    "type": "LogicalOperator",
                    "operator": operator.operator,
                    "left": logical_to_dict(operator.left),
                    "right": logical_to_dict(operator.right)
                }
            if isinstance(operator, Identifier):
                return {
                    "type": "Identifier",
                    "name": operator.name
                }
            if isinstance(operator, Final):
                return {
                    "type": "Final",
                    "value": operator.value
                }
            return {
                "type": "Unknown",
                "value": str(operator)
            }

        def node_to_dict(node):
            if isinstance(node, Projection):
                return {
                    "type": "Projection",
                    "columns": node.columns,
                    "child": node_to_dict(node.child)
                }
            if isinstance(node, Selection):
                return {
                    "type": "Selection",
                    "condition": logical_to_dict(node.condition),
                    "child": node_to_dict(node.child)
                }
            if isinstance(node, JoinOp):
                return {
                    "type": "Join",
                    "condition": logical_to_dict(node.condition),
                    "left_node": node_to_dict(node.left_node),
                    "right_node": node_to_dict(node.right_node)
                }
            return {
                "type": "TableScan",
                "table_name": node.table_name
            }

        return node_to_dict(plan)
