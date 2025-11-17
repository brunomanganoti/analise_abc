import pandas as pd
from pandasql import sqldf
from matplotlib import pyplot as plt
from scipy.stats import f_oneway

df_clientes    = pd.read_csv('data/clientes.csv')
df_itenspedido = pd.read_csv('data/itens_pedido.csv')
df_pedidos     = pd.read_csv('data/pedidos.csv')
df_produtos    = pd.read_csv('data/produtos.csv')

# -- Tratamento de Dados --

# --- Parte 1: Dados de clientes ---
# Percebi que alguns itens da coluna de cidades como São Paulo e Goiânia estão digitados de forma diferente.
# Portanto, o trecho abaixo foi feito para fazer a limpeza desses dados e padronizar o nome dessas cidades, 
# a fim de obter uma análise mais clara e um melhor entendimento das informações. 
# Também foi notado que a base de dados apresenta 'Maranhão' como uma cidade, além de diversas cidades iguais repetidas
# em diferentes estados. Dessa forma, considerei fazer a análise padronizando os nomes das cidades porém mantendo a
# diferença entre os estados. 
# Obs: As cidades registradas como 'Rio' foram consideradas diferentes de 'Rio de Janeiro'.

# 'sao Paulo', 'Sao Paulo' -> 'São Paulo'
df_clientes['cidade'] = df_clientes['cidade'].replace(['sao Paulo', 'Sao Paulo'],'São Paulo')

# 'Maranhao' -> 'Maranhão'
df_clientes['cidade'] = df_clientes['cidade'].replace('Maranhao','Maranhão')

# 'Goiania' -> 'Goiânia'
df_clientes['cidade'] = df_clientes['cidade'].replace('Goiania','Goiânia')

# --- Parte 2: Dados de produtos ---
# No arquivo contendo os dados a respeito dos produtos, também é possível perceber
# duplicações nos nomes de categorias. Dessa forma, também realizei no trecho abaixo 
# o tratamento dessas inconsistências para padronização no nome das categorias,
# evitando duplicação e facilitando a análise.

# 'Decoraçao' -> 'Decoração'
df_produtos['categoria'] = df_produtos['categoria'].replace('Decoraçao','Decoração')

# 'Eletronicos' -> 'Eletrônicos'
df_produtos['categoria'] = df_produtos['categoria'].replace('Eletronicos','Eletrônicos')

# ------------- Análise | Desempenho dos grupos de clientes -------------
# Status de pedido: Confirmado, CANCELADO e Pending

# 1. Qual grupo você escolheria para ser a nossa funcionalidade? Por quê?
# -----------------------------------------------------------------------
# Para esta análise, pesquisei a respeito de Testes AB e decidi fazer da seguinte forma:
# Primeiro, realizei o cálculo da taxa de conversão de cada grupo, considerando o total de clientes
# presente em cada um dividido pelo total de clientes que realizaram a compra (pedido confirmado).
# Ou seja: Conversão = (Total Clientes que compraram / Total Clientes no Grupo) * 100.
# Além disso, também foi deixado em evidência a receita total por grupo para comparação e a
# receita média dos mesmos, finalizando os resultados e possibilitando a análise final.

query_comparacao_grupos = """
SELECT 
    c.grupo AS Grupo,
    COUNT(DISTINCT c.cliente_id) AS Total_Clientes,
    COUNT(DISTINCT 
        CASE WHEN 
        p.status = 'Confirmado' 
        THEN c.cliente_id
        END) AS Total_Compraram,
    ROUND(((COUNT(DISTINCT CASE WHEN p.status = 'Confirmado' THEN c.cliente_id END) 
            / (COUNT(DISTINCT c.cliente_id) * 1.0)) * 100), 2) 
            AS Taxa_Conversao,
    SUM(CASE WHEN 
        p.status = 'Confirmado' 
        THEN p.valor_total 
        END) AS Receita_Total,
    ROUND((SUM(CASE WHEN p.status = 'Confirmado' THEN p.valor_total END)) / 
          (COUNT(DISTINCT c.cliente_id) * 1.0)
          ,2) AS Receita_Media
    FROM df_clientes AS c
    JOIN 
        df_pedidos  AS p
        ON c.cliente_id = p.cliente_id
    GROUP BY c.grupo
    ORDER BY Valor_Total DESC
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('--- Comparação entre os grupos A, B e C ---')
# print(sqldf(query_comparacao_grupos).to_string(index=False))

# Observando os resultados da consulta acima, é possível perceber que o grupo B obteve o melhor desempenho.
# Além de ter a maior receita total, também teve, com uma pequena superioridade, a melhor taxa de conversão, 
# superando o grupo A de controle como também o grupo C variável. Então se formos considerar a receita total
# como métrica principal da análise, é possível determinar o grupo B como vencedor.
# Portanto, apesar da vantagem ser pequena, eu escolheria o grupo B para ser a funcionalidade utilizada.

# --- Confirmação de análise ---
# Para uma confirmação estatística, decidi também realizar um teste ANOVA entre os 3 grupos
# para confirmar que as diferenças vistas anteriormente são de fato relevantes em nosso estudo.
# Este teste foi realizado a partir da biblioteca SciPy.

# Merge clientes + pedidos
df = df_pedidos.merge(df_clientes, on='cliente_id', how='inner')

df_confirmados = df[df['status'] == 'Confirmado']

grupo_A = df_confirmados[df_confirmados['grupo'] == 'A']['valor_total']
grupo_B = df_confirmados[df_confirmados['grupo'] == 'B']['valor_total']
grupo_C = df_confirmados[df_confirmados['grupo'] == 'C']['valor_total']

f_stat, p_value = f_oneway(grupo_A, grupo_B, grupo_C)

# Descomente as linhas abaixo caso queira visualizar os resultados no terminal
# print("f_stat:", f_stat)
# print("p-value:", p_value)

# A partir do teste realizado acima, obtive os seguintes valores:
# f_stat:  29.2
# p-value: 2.3e-13
# Dessa forma, foi possível verificar que o p-value ficou muito abaixo de 0.05, deixando
# evidente que a escolha da funcionalidade do grupo B é estatisticamente justificável,
# já que os outros valores analisados como a receita total e a taxa de conversão já
# apontavam o mesmo como o grupo mais benéfico neste sentido.

# Trecho abaixo realizado para geração de gráficos e visualização dos dados acima

# --- Gráfico comparando taxas de conversão entre os grupos
""" df_conversao_grupos = sqldf(query_comparacao_grupos)
cores = ['#0457ac','#308fac','#37bd79','#a7e237','#f4e604']
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.bar(df_conversao_grupos['Estado'], df_conversao_grupos['Valor_Total'], color=cores, edgecolor='black')
plt.title('Estados com maior receita em vendas', fontsize=16, pad=16)
plt.xlabel('Estado', fontsize=14, labelpad=16)
plt.ylabel('Receita Total (R$)', fontsize=14, labelpad=16)
plt.xticks(rotation=0)
plt.tick_params(axis='x', which='major', pad=10)
plt.margins(x=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout() """

# --- Gráfico comparando porcentagens do total da receita por grupo ---
df_comparacao_grupos = sqldf(query_comparacao_grupos)
cores = ['#6800ff','#0084ff',"#00e677"]
plt.style.use('classic')
plt.figure(figsize=(10,7))
patch, text, pcts = plt.pie(df_comparacao_grupos['Receita_Total'], 
        labels='Grupo ' + df_comparacao_grupos['Grupo'],
        colors=cores, 
        autopct='%1.1f%%',
        startangle=90,
        textprops={'size': 'x-large'},
        explode=(0.045, 0.015, 0.015))
for i, patch in enumerate(patch):
  text[i].set_color(patch.get_facecolor())
plt.setp(text, fontweight='600')
plt.axis('equal')
plt.title('Receita total por Grupo', fontsize=19, pad=16)
# Referência de personalização do gráfico: https://www.pythoncharts.com/matplotlib/pie-chart-matplotlib/

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao1/receita_total_grupo.png')

# OBS: Como o Grupo B foi o escolhido na questão 1, as próximas análises serão
# feitas considerando apenas os clientes ou pedidos que pertencerem a este grupo.

# 2. De acordo com suas análises, o estado do usuário influencia no valor das vendas? 
# -----------------------------------------------------------------------------------
# Para esta análise, decidi comparar as seguintes informações:
# 1. Receita média por estado;
# 2. Taxa de conversão por estado para compras válidas.

query_influencia_estados = """
SELECT
    c.estado AS Estado,
    COUNT(DISTINCT c.cliente_id) AS Total_Clientes,
    COUNT(DISTINCT 
        CASE WHEN 
        p.status = 'Confirmado' 
        THEN c.cliente_id
        END) AS Total_Compraram,
    ROUND(((COUNT(DISTINCT CASE WHEN p.status = 'Confirmado' THEN c.cliente_id END) 
            / (COUNT(DISTINCT c.cliente_id) * 1.0)) * 100), 2) 
            AS Taxa_Conversao,
    COUNT(CASE WHEN
         p.status = 'Confirmado'
         THEN p.pedido_id 
         END) AS Num_Pedidos,
    SUM(CASE WHEN
          p.status = 'Confirmado'
          THEN p.valor_total 
          END) AS Receita_Total,
    ROUND(AVG(CASE WHEN
        p.status = 'Confirmado'
        THEN p.valor_total
        END), 2) AS Receita_Media_Pedido,
    ROUND((SUM(CASE WHEN
          p.status = 'Confirmado'
          THEN p.valor_total END))
          / (COUNT(DISTINCT c.cliente_id) * 1.0), 2) AS Receita_Media_Cliente
    FROM df_clientes AS c
    JOIN 
        df_pedidos  AS p
        ON c.cliente_id = p.cliente_id
    WHERE c.grupo = 'B'
    GROUP BY c.estado
    ORDER BY Receita_Total DESC, Receita_Media_Pedido DESC, Receita_Media_Cliente DESC
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('--- Comparação entre Estados e Receitas: ---')
# print(sqldf(query_influencia_estados).to_string(index=False))

# Ao observar os dados da consulta acima, é possível afirmar que o estado influencia sim
# no valor das vendas. Isso é perceptível pelas diferenças encontradas em diferentes métricas, 
# como a receita média por pedido (AOV), receita média por cliente (ARPU) e receita total.
# Apesar da semelhança entre as taxas de conversão dos estados (todos foram 100%), é
# possível notar a variância entre os valores das métricas citadas acima, com a receita média
# por pedido indo de R$ 3.020,79 (RR) até R$ 3.856,35 (PE), a receita média por cliente
# indo de R$ 14.249,92 (RN) até R$ 25.058,27 (MG) e, por fim, a receita total variando de R$ 131.898 (RS)
# até R$ 464.027 (TO), demonstrando uma diferença muito significativa de aproximadamente 251%.
# Além disso, também é válido apontar a diferença nos números de pedidos por estado, sendo alguns tendo
# entre 38 e 60 pedidos, enquanto os de maior receita ultrapassam 100 pedidos.
# Assim, é possível reafirmar que o estado acaba sim influenciando no valor das vendas, já que se nota
# a diferença de engajamento e comportamento de alguns estados em relação às compras.

# Geração de gráfico para visualização
df_influencia_estados = sqldf(query_influencia_estados)
df_influencia_estados['Porcentagem'] = ((df_influencia_estados['Receita_Total'] / df_influencia_estados['Receita_Total'].sum()) * 100).round(2)
df_influencia_estados = df_influencia_estados.head(10).sort_values(by='Porcentagem', ascending=True)

cores = ['#e07a5f', '#3d405b', '#81b29a', '#f2cc8f', "#8c9491"]
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.barh(df_influencia_estados['Estado'], df_influencia_estados['Porcentagem'], color=cores, edgecolor='black')
plt.title('10 estados com maior participação da receita total', fontsize=16, pad=16)
plt.xlabel('Percentual (%)', fontsize=14, labelpad=16)
plt.ylabel('Estado', fontsize=14, labelpad=16)
plt.xticks(rotation=0)
plt.tick_params(axis='y', which='major', pad=10)
plt.margins(y=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao2/estados_percentual.png')

# 3. Quais são os estados e cidades com maior valor em vendas? Liste-os em ordem decrescente.
# -------------------------------------------------------------------------------------------
# Como citado anteriormente, para essa análise foram padronizados os nomes de cidades e mantidos os
# diferentes estados que possuíam cidades com mesmo nome.
# Dessa forma, realizei uma query para cada consulta solicitada, sendo uma com os estados com maior
# valor em vendas (query_estados) e a outra com as cidades com maior valor em vendas (query_cidades).
# Esta verificação também contou apenas os pedidos que estivessem com o status de 'Confirmado', assim
# deixando de incluir pedidos não finalizados e outros que possam ser cancelados (pending).

query_estados = """
SELECT 
    c.estado AS Estado,
    SUM(p.valor_total) AS Valor_Total 
    FROM df_clientes AS c
    JOIN 
        df_pedidos  AS p
        ON c.cliente_id = p.cliente_id
    WHERE p.status = 'Confirmado' AND
          c.grupo  = 'B'
    GROUP BY c.estado
    ORDER BY Valor_Total DESC
    LIMIT 5
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('--- 5 estados com maior receita: ---')
# print(sqldf(query_estados).to_string(index=False))

# Trecho abaixo foi usado para gerar o gráfico utilizado no arquivo questoes_analise.md (questão 3)
df_top_estados = sqldf(query_estados)
cores = ['#0457ac','#308fac','#37bd79','#a7e237','#f4e604']
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.bar(df_top_estados['Estado'], df_top_estados['Valor_Total'], color=cores, edgecolor='black')
plt.title('Estados com maior receita em vendas', fontsize=16, pad=16)
plt.xlabel('Estado', fontsize=14, labelpad=16)
plt.ylabel('Receita Total (R$)', fontsize=14, labelpad=16)
plt.xticks(rotation=0)
plt.tick_params(axis='x', which='major', pad=10)
plt.margins(x=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao3/top_estados.png')

query_cidades = """
SELECT
    c.cidade AS Cidade,
    c.estado AS Estado,
    SUM(p.valor_total) AS Valor_Total
    FROM df_clientes AS c
    JOIN 
        df_pedidos  AS p
        ON c.cliente_id = p.cliente_id
    WHERE p.status = 'Confirmado' AND
          c.grupo  = 'B'
    GROUP BY c.cidade, c.estado
    ORDER BY Valor_Total DESC
    LIMIT 5
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('\n--- 5 cidades com maior receita: ---')
# print(sqldf(query_cidades).to_string(index=False))

# Trecho abaixo foi usado para gerar o gráfico utilizado no arquivo questoes_analise.md (questão 3)
df_top_cidades = sqldf(query_cidades)

# Aqui criei uma nova coluna para separar cidades de mesmo nome com estados diferentes 
df_top_cidades['Cidade_UF'] = df_top_cidades['Cidade'] + ' (' + df_top_cidades['Estado'] + ')' 

cores = ['#e9724d','#d6d727','#92cad1','#79ccb3','#868686']
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.bar(df_top_cidades['Cidade_UF'], df_top_cidades['Valor_Total'], color=cores, edgecolor='black')
plt.title('Cidades com maior receita em vendas', fontsize=16, pad=16)
plt.xlabel('Cidade (UF)', fontsize=14, labelpad=16)
plt.ylabel('Receita Total (R$)', fontsize=14, labelpad=16)
plt.xticks(rotation=0)
plt.tick_params(axis='x', pad=10)
plt.margins(x=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao3/top_cidades.png')

# 4. A categoria do produto ou quantidade de itens do pedido influencia no status no pedido?
# ------------------------------------------------------------------------------------------
# Parte 1: Influência da categoria
# Para poder responder esta questão, decidi fazer duas comparações em duas consultas diferentes:
# 1. Número de pedidos confirmados e cancelados por categoria;
# 2. Número de pedidos confirmados e cancelados por número de itens no pedido.
# Junto a essa quantidade, também vou calcular em uma outra coluna a porcentagem
# desses pedidos confirmados e cancelados. Abaixo estão as queries escritas:

# Análise da influência da categoria no status do pedido
query_influencia_categoria = """
SELECT 
    prod.categoria AS Categoria,
    COUNT(DISTINCT p.pedido_id) AS Num_Pedidos,
    COUNT(DISTINCT CASE WHEN
         p.status = 'Confirmado'
         THEN p.pedido_id
         END) AS Num_Confirmados,
    COUNT(DISTINCT CASE WHEN
         p.status = 'CANCELADO'
         THEN p.pedido_id
         END) AS Num_Cancelados,
    COUNT(DISTINCT CASE WHEN
         p.status = 'Pending'
         THEN p.pedido_id
         END) AS Num_Pendentes,
    ROUND(COUNT(DISTINCT CASE WHEN
         p.status = 'CANCELADO'
         THEN p.pedido_id
         END) * 1.0
         / COUNT(DISTINCT p.pedido_id) * 100, 2) AS Taxa_Cancelamento
    FROM  
        df_produtos AS prod
    JOIN 
        df_itenspedido AS i
        ON i.produto_id = prod.produto_id
    JOIN 
        df_pedidos AS p
        ON p.pedido_id = i.pedido_id
    GROUP BY prod.categoria
    ORDER BY Num_Pedidos DESC
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('\n--- Comparação de pedidos entre categorias: ---')
# print(sqldf(query_influencia_categoria).to_string(index=False))

# Com a consulta acima, podemos dizer a categoria do produto influencia sim no
# status do pedido. É possível concluir isso ao perceber a diferença entre a menor
# taxa de cancelamento (15.3), da categoria 'Brinquedos' e a maior taxa de cance-
# lamento (17.12), da categoria 'Roupas'.
# Esta diferença provavelmente se dá ao fato das roupas terem uma maior proba-
# bilidade de virem com algum defeito ou insatisfação com o tamanho pedido,
# gerando assim mais trocas e devoluções em relação aos brinquedos por exemplo,
# que são compras mais específicas de forma geral.

# Geração dos gráficos referentes a influência da categoria no status do pedido
df_influencia_categoria = sqldf(query_influencia_categoria)

# 1° Gráfico: Total de Pedidos + Status
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.bar(df_influencia_categoria['Categoria'], df_influencia_categoria['Num_Pendentes'],
        bottom=df_influencia_categoria['Num_Cancelados'] + df_influencia_categoria['Num_Confirmados'],
         color='#ffb703', edgecolor='black', label='Pendentes')
plt.bar(df_influencia_categoria['Categoria'], df_influencia_categoria['Num_Cancelados'],
        bottom=df_influencia_categoria['Num_Confirmados'], color='#ff6666', edgecolor='black', label='Cancelados')
plt.bar(df_influencia_categoria['Categoria'], df_influencia_categoria['Num_Confirmados'], 
        color='#6aa84f', edgecolor='black', label='Confirmados')
plt.title('Comparação de pedidos entre categorias', fontsize=16, pad=16)
plt.xlabel('Categoria', fontsize=14, labelpad=16)
plt.ylabel('Total de Pedidos', fontsize=14, labelpad=16)
plt.xticks(rotation=0)
plt.tick_params(axis='x', pad=10)
plt.margins(x=0.03)
plt.grid(True, linestyle='--')
plt.legend()
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao4/influencia_categoria_pedidos.png')

df_influencia_categoria = df_influencia_categoria.sort_values(by='Taxa_Cancelamento', ascending=False)

# 2° Gráfico: Taxa de cancelamento
plt.style.use('classic')
plt.figure(figsize=(12,8))
plt.plot(df_influencia_categoria['Categoria'], df_influencia_categoria['Taxa_Cancelamento'], 
         marker='o', markerfacecolor='#1400c9', color='#cb05f2', markersize='8')
plt.title('Taxa de cancelamento por categoria', fontsize=16, pad=16, color='#db261d')
plt.xlabel('Categoria', fontsize=14, labelpad=16, color="#db261d")
plt.ylabel('Taxa de Cancelamento (%)', fontsize=14, labelpad=16, color='#db261d')
plt.xticks(rotation=0)
plt.tick_params(axis='x', pad=10)
plt.margins(x=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao4/influencia_categoria_cancelamento.png')

# Parte 2: Influência da quantidade de itens no pedido
# Para esta análise, separei os pedidos por categorias específicas de 
# tamanho, sendo pedidos de tamanho pequeno (com 1 a 3 itens), pedidos
# de tamanho médio (com 3 a 6 itens) e pedidos de tamanho grande
# (com 7 itens ou mais). A partir disso, calculei a taxa de cancelamento
# referente a cada uma dessas categorias criadas para realizar as observações.

query_influencia_itens = """
WITH SomaItens AS 
    (SELECT 
        pedido_id, 
        SUM(quantidade) AS total_itens
    FROM df_itenspedido
    GROUP BY pedido_id),
Categorias AS 
    (SELECT 
        p.pedido_id,
        p.status,
        s.total_itens,
        CASE 
            WHEN s.total_itens <= 3 THEN 'Pequeno (1-3 itens)'
            WHEN s.total_itens <= 6 THEN 'Médio (3-6 itens)'
            ELSE 'Grande (7-+ itens)'
        END AS Tamanho_Pedido
    FROM df_pedidos p
    JOIN SomaItens AS s 
        ON p.pedido_id = s.pedido_id)
SELECT 
    Tamanho_Pedido,
    COUNT(*) as Num_Pedidos,
    SUM(CASE WHEN status = 'Confirmado' THEN 1 ELSE 0 END) AS Num_Confirmados,
    SUM(CASE WHEN status = 'CANCELADO'  THEN 1 ELSE 0 END) AS Num_Cancelados,
    SUM(CASE WHEN status = 'Pending'    THEN 1 ELSE 0 END) AS Num_Pendentes,
    ROUND((SUM(CASE WHEN status = 'CANCELADO' THEN 1.0 ELSE 0.0 END) 
         / COUNT(*)) * 100, 2) AS Taxa_Cancelamento
FROM Categorias
GROUP BY Tamanho_Pedido
ORDER BY Tamanho_Pedido;
"""
# Caso queira ver os resultados pelo terminal, descomente as linhas abaixo e rode o arquivo (py analise.py):
# print('\n--- Comparação entre número de itens do pedido: ---')
print(sqldf(query_influencia_itens).to_string(index=False))

# Com a consulta acima, temos que a maior taxa de cancelamento (17.92%) se trata
# de pedidos pequenos, com 1 a 3 itens  e a menor taxa de cancelamento (16.17%)
# pertence a pedidos grandes (7 itens ou mais). Portanto, essa informação
# nos permite afirmar que, apesar da diferença ser baixa, o número de itens
# do pedido acaba sim influenciando o status do mesmo, já que pedidos maiores
# acabam sendo de certa forma compras mais decididas, gerando uma taxa de can-
# celamento menor em relação a pedidos médios ou pequenos.

# Geração dos gráfico referente a influência do número de itens no status do pedido
df_influencia_itens = sqldf(query_influencia_itens)

valores_externo = []
cores_externo = []
labels_para_legenda = []

cor_conf = '#27ae60' # Verde
cor_canc = '#c0392b' # Vermelho
cor_pend = '#95a5a6' # Cinza

plt.figure(figsize=(10, 10))
plt.pie(valores_externo, radius=1.0, colors=cores_externo, labels=labels_para_legenda,
        wedgeprops=dict(width=0.3, edgecolor='white'), labeldistance=None)
plt.pie(df_influencia_itens['Num_Pedidos'], radius=0.7, labels=df_influencia_itens['Tamanho_Pedido'], 
        labeldistance=0.6, colors=['#5dade2', '#2980b9', '#1a5276'], 
        wedgeprops=dict(width=0.3, edgecolor='white'),
        textprops={'color': 'white', 'weight': 'bold', 'fontsize': 11})
plt.legend(loc='center', title="Status", frameon=False)
plt.title('Distribuição: Tamanho vs. Status')
plt.tight_layout()
plt.savefig('graficos/questao5/influencia_itens.png')

# 5. Outras métricas
# ------------------

