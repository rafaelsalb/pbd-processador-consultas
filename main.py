from pprint import pprint

from catalog import Catalog
from lexical import LexicalAnalyzer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from syntactic import SyntacticAnalyzer


def main():
    # analyzer = LexicalAnalyzer()
    # tokens = analyzer.analyze(
    #     # Select cliente.nome, pedido.idPedido, pedido.DataPedido, pedido.ValorTotalPedido
    #     # from Cliente Join pedido on cliente.idcliente = pedido.Cliente_idCliente
    #     # where cliente.TipoCliente_idTipoCliente = 1 and pedido.ValorTotalPedido = 0;
    #     """select id_cliente = 2"""
    # )
    # syn_analyzer = SyntacticAnalyzer(tokens)
    # syn_analyzer.parse()

    code = """SELECT Cliente.Nome, Pedido.idPedido, Pedido.DataPedido, Pedido.ValorTotalPedido
FROM Cliente JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente
WHERE Cliente.TipoCliente_idTipoCliente = 1 AND Pedido.ValorTotalPedido = 0;"""
    # code = "SELECT idCliente, Nome FROM Cliente WHERE idCliente >= 1 AND TipoCliente_idTipoCliente = 2"
    parser = Parser(code)
    tree = parser.parse()
    pprint(tree)
    semantic_analyzer = SemanticAnalyzer()
    print(semantic_analyzer.context.catalog)
    semantic_analyzer.analyze(tree)


if __name__ == "__main__":
    main()
