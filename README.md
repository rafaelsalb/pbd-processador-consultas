Before:

SELECT Cliente.Nome, Pedido.idPedido, Pedido.DataPedido, Pedido.ValorTotalPedido

FROM Cliente

JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente

WHERE Cliente.TipoCliente_idTipoCliente = 1 AND Pedido.ValorTotalPedido = 0;

After:

SELECT Cliente.Nome, Pedido.idPedido, Pedido.DataPedido, Pedido.ValorTotalPedido

FROM ( SELECT * FROM Cliente WHERE Cliente.TipoCliente = 1 )

JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente

WHERE Pedido.ValorTotalPedido = 0;

Further:

SELECT Cliente.Nome, Pedido.idPedido, Pedido.DataPedido, Pedido.ValorTotalPedido

FROM ( SELECT * FROM Cliente WHERE Cliente.TipoCliente = 1 )

JOIN ( SELECT * FROM Pedido WHERE Pedido.ValorTotalPedido = 0 ) ON Cliente.idCliente = Pedido.Cliente_idCliente;
