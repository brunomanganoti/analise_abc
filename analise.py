import pandas as pd
from pandasql import sqldf
from matplotlib import pyplot as plt
from scipy.stats import f_oneway

df_clientes    = pd.read_csv('data/clientes.csv')
df_itenspedido = pd.read_csv('data/itens_pedido.csv')
df_pedidos     = pd.read_csv('data/pedidos.csv')
df_produtos    = pd.read_csv('data/produtos.csv')

# -- Tratamento de Dados --
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
    ROUND((SUM(CASE WHEN p.status = 'Confirmado' THEN p.valor_total ELSE 0 END)) / 
          (COUNT(DISTINCT c.cliente_id) * 1.0)
          ,2) AS Receita_Media
    FROM df_clientes AS c
    JOIN df_pedidos  AS p
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

# 2. De acordo com suas análises, o estado do usuário influencia no valor das vendas? 
# -----------------------------------------------------------------------------------
# Para esta análise, decidi seguir um fluxo contendo duas análises:
# 1. Comparação de receita média por estado;
# 2. Comparação da taxa de conversão por estado para compras válidas.

query_influencia_estados = """
SELECT

"""

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
    JOIN df_pedidos  AS p
    ON c.cliente_id = p.cliente_id
    WHERE p.status = 'Confirmado'
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
    JOIN df_pedidos  AS p
    ON c.cliente_id = p.cliente_id
    WHERE p.status = 'Confirmado'
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
plt.tick_params(axis='x', which='major', pad=10)
plt.margins(x=0.05)
plt.grid(True, linestyle='--')
plt.tight_layout()

# Descomente a linha abaixo caso queira salvar novamente o gráfico gerado.
# plt.savefig('graficos/questao3/top_cidades.png')

# 4. A categoria do produto ou quantidade de itens do pedido influencia no status no pedido?
# ------------------------------------------------------------------------------------------


# 5. Outras métricas
# ------------------
