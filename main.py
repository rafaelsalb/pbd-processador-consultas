from execution_graph import ExecutionGraph
from optimizer import TreeOptimizer
from parser import Parser
from relational import ExecutionPlan
from semantic_analyzer import SemanticAnalyzer
from tree_traversal import breadth_first_traversal


def main():
    code = """SELECT Cliente.Nome, Pedido.idPedido, Pedido.DataPedido, Pedido.ValorTotalPedido
FROM Cliente JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente
WHERE Cliente.TipoCliente_idTipoCliente = 1 AND Pedido.ValorTotalPedido = 0;"""
    # code = "SELECT Cliente.idCliente, Cliente.Nome FROM Cliente WHERE Cliente.idCliente >= 1 AND Cliente.TipoCliente_idTipoCliente = 2;"
    parser = Parser(code)
    tree = parser.parse()
    # pprint(tree)
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.analyze(tree)
    planner = ExecutionPlan()
    plan = planner.build(tree)
    for i, node in enumerate(breadth_first_traversal(plan)):
        print(f"Node {i}: {node}")
    print("Plano de Execução:")
    # pprint(plan)
    # graph = ExecutionGraph.from_plan(plan)
    optimizer = TreeOptimizer(plan)
    optimized_plan = optimizer.optimize(plan)
    print("\nPlano de Execução Otimizado:")
    for i, node in enumerate(breadth_first_traversal(optimized_plan)):
        print(f"Node {i}: {node}")

    # print("\n" * 2)
    # print(ExecutionGraph().jsonify(plan)) # visualize(plan)

if __name__ == "__main__":
    main()
