class Catalog:
    def __init__(self, schema=None):
        """
        • Categoria (idCategoria, Descricao )
        • Produto (idProduto, Nome, Descricao, Preco, QuantEstoque, Categoria_idCategoria)
        • TipoCliente ( idTipoCliente, Descricao)
        • Cliente (idCliente, Nome, Email, Nascimento, Senha, TipoCliente_idTipoCliente, DataRegistro)
        • TipoEndereco (idTipoEndereco , Descricao)
        • Endereco (idEndereco, EnderecoPadrao, Logradouro, Numero, Complemento, Bairro, Cidade, UF,
        CEP, TipoEndereco_idTipoEndereco, Cliente_idCliente )
        • Telefone (Numero, Cliente_idCliente)
        • Status (idStatus, Descricao)
        • Pedido (idPedido, Status_idStatus, DataPedido, ValorTotalPedido, Cliente_idCliente)
        • Pedido_has_Produto(idPedidoProduto, Pedido_idPedido, Produto_idProduto, Quantidade,
        PrecoUnitario)
        """
        self.schema = schema if schema is not None else (
            {
                'Categoria': {
                    'idCategoria': int,
                    'Descricao': str,
                },
                'Produto': {
                    'idProduto': int,
                    'Nome': str,
                    'Descricao': str,
                    'Preco': float,
                    'QuantEstoque': float,
                    'Categoria_idCategoria': int,
                },
                'TipoCliente': {
                    'idTipoCliente': int,
                    'Descricao': str,
                },
                'Cliente': {
                    'idCliente': int,
                    'Nome': str,
                    'Email': str,
                    'Nascimento': str,
                    'Senha': str,
                    'TipoCliente_idTipoCliente': int,
                    'DataRegistro': str,
                },
                'TipoEndereco': {
                    'idTipoEndereco': int,
                    'Descricao': str,
                },
                'Endereco': {
                    'idEndereco': int,
                    'EnderecoPadrao': int,
                    'Logradouro': str,
                    'Numero': str,
                    'Complemento': str,
                    'Bairro': str,
                    'Cidade': str,
                    'UF': str,
                    'CEP': str,
                    'TipoEndereco_idTipoEndereco': int,
                    'Cliente_idCliente': int,
                },
                'Telefone': {
                    'Numero': str,
                    'Cliente_idCliente': int,
                },
                'Status': {
                    'idStatus': int,
                    'Descricao': str,
                },
                'Pedido': {
                    'idPedido': int,
                    'Status_idStatus': int,
                    'DataPedido': str,
                    'ValorTotalPedido': float,
                    'Cliente_idCliente': int,
                },
                'Pedido_has_Produto': {
                    'idPedidoProduto': int,
                    'Pedido_idPedido': int,
                    'Produto_idProduto': int,
                    'Quantidade': float,
                    'PrecoUnitario': float,
                },
            }
        )

    def has_table(self, name: str) -> bool:
        return name in self.schema

    def has_column(self, table: str, column: str) -> bool:
        print(f"Checking if column {column} exists in table {table}...")
        return self.has_table(table) and column in self.schema[table]

    def get_column_type(self, table: str, column: str):
        if self.has_column(table, column):
            return self.schema[table][column]

    def __repr__(self):
        return str(self.schema)
