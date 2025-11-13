import pandas as pd
from pandasql import sqldf
from matplotlib import pyplot

df_clientes    = pd.read_csv('data/clientes.csv')
df_itenspedido = pd.read_csv('data/itens_pedido.csv')
df_pedidos     = pd.read_csv('data/pedidos.csv')
df_produtos    = pd.read_csv('data/produtos.csv')

query = """
SELECT * FROM df_clientes
WHERE estado = 'SP'
LIMIT 10
"""

print(sqldf(query))