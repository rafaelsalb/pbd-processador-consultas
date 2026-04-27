from pprint import pprint

from lexical import LexicalAnalyzer
from parser import Parser
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

#     code = """SELECT cliente.nome, pedido.idPedido, pedido.DataPedido, pedido.ValorTotalPedido
# FROM Cliente JOIN pedido ON cliente.idcliente = pedido.Cliente_idCliente
# WHERE cliente.TipoCliente_idTipoCliente = 1 and pedido.ValorTotalPedido = 0;"""
    code = "SELECT idCliente, Nome FROM Cliente WHERE idCliente >= 1 AND TipoCliente_idTipoCliente = 2"
    parser = Parser(code)
    tree = parser.parse()
    pprint(tree)


if __name__ == "__main__":
    main()
