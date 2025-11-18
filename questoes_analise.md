<h1 align="center">Teste Técnico: Análise de Teste A/B/C</h1>

# Observações
* Este arquivo foi utilizado para conter apenas um resumo das respostas;
* O arquivo de código `analise.py` apresenta toda a lógica por trás das respostas e outros comentários explicativos.

# 📝 Perguntas

## 1️⃣ Qual grupo você escolheria para ser a nossa funcionalidade? Por quê?

* **Escolha:** Grupo B.
* **Motivo:** A análise indicou que o Grupo B obteve o melhor desempenho geral. Além de apresentar a maior receita total, também superou os grupos A (Controle) e C em taxa de conversão.
* **Validação Estatística:** Foi realizado um teste ANOVA (One-Way) para confirmar a significância dos resultados, obtendo-se um **f-stat de 29.2** e um **p-value de 2.3e-13**. Como o p-value é muito inferior a 0.05, a superioridade do Grupo B é estatisticamente relevante, assim podendo justificar sua escolha.

<div>
   <img src="graficos\questao1\percentual_total_grupo.png" alt="" width="450">
   <img src="graficos\questao1\receita_total_grupo.png" alt="" width="475">
</div>

## 2️⃣ De acordo com suas análises, o estado do usuário influencia no valor das vendas?

* **Sim, influencia.**
* Embora a taxa de conversão tenha se mantido consistente (100% em vendas confirmadas), houve uma variação significativa nas métricas de receita entre os estados.
* **Variação de Receita:** A receita total variou cerca de **251%** entre o estado com menor desempenho (RS - R$ 131.898) e o com maior desempenho (TO - R$ 464.027).
* **Ticket Médio:** Também foi notada diferença no comportamento de gasto, com a Receita Média por Pedido variando de R$ 3.020,79 (em RR) até R$ 3.856,35 (em PE).

<div>
   <img src="graficos\questao2\estados_percentual.png" alt="" width="450">
</div>

## 3️⃣ Quais são os estados e cidades com maior valor em vendas? Liste-os em ordem decrescente.

* **Análise:** A consulta foi realizada filtrando apenas o Grupo B e pedidos confirmados.
* **Top Estados:** O estado de **Tocantins (TO)** se destacou com a maior receita total (R$ 464.027), seguido por outros estados com alto volume.
* **Cidades:** Foi realizado um tratamento de dados para distinguir cidades com mesmo nome em estados diferentes (ex: criar a coluna `Cidade (UF)`).
* *(Obs: A lista completa dos Top 5 Estados e Cidades é gerada diretamente pela execução do script `analise.py` e visualizada nos gráficos da pasta `graficos/questao3/`).*

<div>
   <img src="graficos\questao3\top_cidades.png" alt="" width="475">
   <img src="graficos\questao3\top_estados.png" alt="" width="475">
</div>

## 4️⃣ A categoria do produto ou quantidade de itens do pedido influencia no status no pedido?

* **Sim, ambos influenciam.**
    1.  **Categoria:** A categoria **Roupas** apresentou a maior taxa de cancelamento (**17.57%**), provavelmente devido a problemas de tamanho ou caimento. Em contraste, **Brinquedos** teve a menor taxa (**16.46%**), indicando compras mais assertivas.
    2.  **Quantidade de Itens:** O tamanho do pedido afeta inversamente o cancelamento. Pedidos **Pequenos (1-3 itens)** tiveram a menor taxa de cancelamento (**14.81%**), enquanto Pedidos **Grandes (7+ itens)** tiveram a maior (**17.69%**), sugerindo que compras menores tendem a ser mais decididas.

<div>
   <img src="graficos\questao4\influencia_categoria_cancelamento.png" alt="" width="485">
   <img src="graficos\questao4\influencia_categoria_pedidos.png" alt="" width="485">
   <img src="graficos\questao4\influencia_itens.png" alt="" width="440">
</div>

## 5️⃣ Outras métricas

Para finalizar a análise, foram extraídas métricas adicionais focadas no Grupo B para a construção de um Dashboard no Power BI. As métricas escolhidas foram:

1.  **Ticket Médio:** Valor médio gasto por pedido confirmado.
2.  **Status dos Pedidos:** Visão geral da eficiência operacional (Confirmados, Pendentes e Cancelados).
3.  **Sazonalidade:** Evolução do faturamento ao longo dos meses.
4.  **Geografia:** Estados com maior volume de vendas.

*(Os dados dessas métricas foram exportados para a pasta `PowerBI/data` em formato .csv)*
<br>
*(O dashboard gerado pode ser encontrado em `PowerBI/dashboard_teste.pbix`)*