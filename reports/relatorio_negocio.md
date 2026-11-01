# Relatório de Negócio: NPS Preditivo

**Tech Challenge · Fase 1**

Este relatório responde aos itens do enunciado do Tech Challenge em linguagem de negócio, e os números citados vêm dos notebooks da pasta `notebooks/`, onde cada cálculo pode ser conferido e reproduzido.

---

## Resumo executivo

O NPS (Net Promoter Score, ou índice de recomendação do cliente) da empresa está em **-80**, o que significa que, de cada 100 clientes, 84 são detratores e apenas 4 são promotores.

A análise mostra que essa insatisfação não está ligada ao preço nem ao perfil do cliente, e sim a dois aspectos da operação: o **atraso na entrega** e os **problemas no atendimento**. Os principais achados são:

- O atraso é o fator mais forte, e existe um ponto de ruptura em **2 dias de atraso**, a partir do qual 88% dos clientes se tornam detratores. Hoje, **64% dos pedidos** estão nessa faixa.
- O prazo total de entrega, ao contrário do atraso, não altera a satisfação, o que indica que o cliente aceita esperar quando o prazo prometido é cumprido.
- **92% dos detratores** passaram por pelo menos um problema operacional, seja atraso de 2 dias ou mais, 4 reclamações ou mais, ou 2 contatos ou mais com o atendimento.
- Um modelo de classificação, treinado apenas com dados disponíveis antes da pesquisa, identifica os clientes em risco com AUC (Area Under the Curve, ou área sob a curva) de 0,87, e no grupo classificado como "alto risco" todos os clientes se tornaram detratores.
- Uma simulação com os dados históricos indica que limitar o atraso a 1 dia e reduzir as reclamações poderia levar o NPS de -80 para cerca de **-41**, estimativa que precisa ser validada com um piloto.

Seguindo o framework ABT (And–But–Therefore, ou "e, mas, portanto") apresentado na Aula 4, a história deste trabalho pode ser resumida assim: a empresa cresceu e passou a atender um volume maior de pedidos, **mas** 84% dos clientes se tornaram detratores, principalmente por atraso na entrega e por problemas no atendimento, **portanto** a prioridade é cumprir o prazo prometido e agir sobre os pedidos em risco antes que a pesquisa seja aplicada.

---

## 1. Entendimento do negócio

### Qual problema de negócio está sendo resolvido?

A empresa cresceu com o avanço do e-commerce e passou a lidar com mais pedidos, entregas e contatos de clientes, mas esse crescimento veio acompanhado de uma grande variação no NPS, com alguns clientes se tornando promotores e outros detratores mesmo diante de indicadores operacionais parecidos.

O problema tem duas partes que se complementam:

1. **Diagnóstico:** a empresa não sabe quais fatores operacionais de fato explicam a insatisfação, e sem esse entendimento os investimentos em melhoria ficam sem direção.
2. **Antecipação:** o NPS só é coletado depois do encerramento da jornada de compra, quando o cliente já formou sua opinião, o que impede a empresa de agir de forma preventiva.

Usando a classificação de perguntas analíticas da Aula 1, o trabalho percorre os quatro níveis: a pergunta **descritiva** (qual é o NPS hoje e como ele se distribui), a **diagnóstica** (quais fatores explicam os detratores), a **preditiva** (qual a chance de um cliente se tornar detrator) e a **prescritiva** (quais ações a empresa deve priorizar).

A pergunta orientadora, formulada de forma específica e testável, é a seguinte:

> **Quais fatores operacionais de pedido, logística e atendimento explicam por que um cliente se torna detrator, e como identificar esse risco antes da aplicação da pesquisa de NPS?**

### Por que o NPS é importante para um e-commerce?

O NPS mede a disposição do cliente em recomendar a empresa, e não apenas a satisfação com uma compra isolada, o que o torna um indicador de lealdade. Para um e-commerce, essa medida é importante por quatro motivos:

- **Recompra:** manter um cliente costuma custar menos do que conquistar um novo, e o NPS indica quais clientes tendem a voltar.
- **Reputação pública:** no comércio digital, as avaliações ficam visíveis em marketplaces, sites de reclamação e redes sociais, e influenciam quem ainda não comprou.
- **Simplicidade:** é uma pergunta única, fácil de acompanhar ao longo do tempo e de comparar com a concorrência.
- **Priorização:** quando cruzado com dados da operação, mostra em que ponto a experiência se quebra e onde investir primeiro.

### Quais áreas podem se beneficiar dos insights?

| Área | Como pode usar os insights |
|---|---|
| **Logística** | Priorizar pedidos com risco de atraso, recalibrar os prazos prometidos e avaliar transportadoras |
| **Atendimento (SAC, Serviço de Atendimento ao Consumidor)** | Resolver o problema no primeiro contato, criar fila prioritária e definir um SLA (Service Level Agreement, ou acordo de nível de serviço) de resolução |
| **Experiência do Cliente** | Fazer contato proativo e oferecer compensação aos clientes de alto risco antes da pesquisa |
| **Produto / Marketplace** | Investigar a origem das reclamações, como qualidade do produto, descrição do anúncio e seller (vendedor parceiro) |
| **Pricing (precificação)** | Considerar que desconto e frete não aparecem como alavancas de satisfação nesta base, o que evita gastos sem retorno |
| **CRM (Customer Relationship Management, ou gestão de relacionamento com o cliente) / Marketing** | Segmentar ações pela situação do pedido, e não pelo perfil demográfico, e incentivar a indicação por parte dos promotores |
| **Liderança / Estratégia** | Acompanhar o NPS projetado antes da pesquisa e priorizar investimentos |

### Reflexão: como o NPS impacta a recompra, o boca a boca e o market share

**Recompra.** Na base analisada, 100% dos promotores recompraram em até 30 dias, enquanto nenhum detrator voltou a comprar, e entre os neutros a recompra foi de 38%. Isso mostra que converter um detrator em neutro ou promotor tem efeito direto sobre a receita recorrente, que no e-commerce é o que sustenta o custo de aquisição do cliente.

**Boca a boca.** O promotor recomenda a empresa sem custo, trazendo novos clientes de forma orgânica, enquanto o detrator faz o movimento oposto e, no ambiente digital, sua avaliação negativa fica acessível a muitos compradores. Com NPS de -80, a empresa tem cerca de 19 detratores para cada promotor.

**Market share (participação de mercado).** No e-commerce, trocar de loja exige pouco esforço do cliente, e um NPS baixo e persistente tende a provocar a perda de clientes para a concorrência a cada compra, uma dependência maior de mídia paga para repor a base e, com o tempo, a perda de participação de mercado.

### Indicadores de mercado que complementariam a análise

| Indicador | Por que ajuda |
|---|---|
| **Benchmark (referência de mercado) de NPS do setor** | Permite medir a distância em relação à concorrência |
| **Reputação em sites de reclamação** (nota e índice de solução) | Mostra o reflexo público da insatisfação |
| **Avaliações em marketplaces e lojas de aplicativos** | Acompanha a reputação de forma contínua |
| **SLA logístico por transportadora e região** (% entregue no prazo) | Liga-se diretamente ao principal fator do NPS encontrado nesta análise |
| **Prazo prometido pelos concorrentes** | Ajuda a calibrar promessas realistas e competitivas |
| **FCR (First Contact Resolution, ou resolução no primeiro contato)** | Mede a eficiência do atendimento |
| **Taxa de recompra, churn (taxa de abandono de clientes) e LTV (Lifetime Value, ou valor do cliente ao longo do relacionamento)** | Traduz o NPS em valor financeiro |
| **CAC (Custo de Aquisição de Cliente)** | Mostra quanto custa repor um cliente perdido |
| **Share of search (participação nas buscas)** | Indica o efeito da reputação sobre a participação de mercado |

---

## 2. Definição da target (variável alvo)

### Qual variável representa a satisfação do cliente?

A variável é **`nps_score`**, a nota de 0 a 10 dada pelo cliente à pergunta "Quanto você recomendaria a empresa a um amigo?". A partir dela foram criadas duas variáveis derivadas:

- **Categoria NPS:** Detrator (nota menor que 7), Neutro (de 7 a menos de 9) e Promotor (9 ou mais).
- **Alvo do modelo de classificação:** `is_detractor`, que vale 1 quando a nota é menor que 7 e 0 nos demais casos.

### Por que ela foi escolhida?

A nota NPS foi escolhida porque é o indicador que a área de Experiência do Cliente já acompanha, porque mede lealdade e recomendação, e não apenas a satisfação com uma interação, e porque tem ligação comprovada com a recompra na própria base. O foco em detratores responde diretamente à dor do negócio, que é perder clientes e reputação.

O CSAT (Customer Satisfaction Score, ou índice de satisfação do cliente) também está disponível na base, mas foi descartado como alvo. Enquanto o NPS mede a relação do cliente com a marca, o CSAT mede a satisfação com uma interação específica, e ele é coletado no mesmo momento que o NPS, o que impede seu uso para antecipar o resultado.

### Em que momento da jornada essa informação é coletada?

A nota é coletada **depois do encerramento da jornada de compra**, ou seja, após a entrega, os eventuais contatos com o SAC e a resolução de problemas. Por esse motivo, o modelo preditivo usa apenas informações disponíveis antes desse momento.

```
Compra → Pagamento → Despacho → Entrega (atraso?) → SAC (reclamações?) → [Pesquisa NPS] → Recompra
                                  ▲ o modelo atua aqui, antes da pesquisa ▲
```

### Existe risco de usar essa variável de forma inadequada?

Sim, e os principais riscos identificados são:

1. **Vazamento de informação (*data leakage*):** as variáveis `csat_internal_score` e `repeat_purchase_30d` são medidas junto com o NPS ou depois dele. Usá-las para prever o NPS inflaria artificialmente o desempenho do modelo, e por isso as duas foram excluídas da modelagem.
2. **Viés de resposta:** a base contém apenas clientes que responderam à pesquisa, e clientes muito insatisfeitos tendem a responder mais, o que pode fazer o NPS medido não representar toda a base de clientes.
3. **Uso individual da nota:** o NPS é um indicador de grupo, e usá-lo para avaliar ou punir uma pessoa, como um entregador ou um atendente, pode gerar distorções, como pedir ao cliente uma nota alta.
4. **Confundir correlação com causa:** a análise mostra associações entre variáveis, e as ações recomendadas precisam ser testadas antes de virar regra.
5. **Regra de corte:** a base traz notas com casas decimais, como 6,9, enquanto uma pesquisa NPS tradicional usa números inteiros. A regra adotada aqui (6,9 é detrator e 7,0 é neutro) precisa ser confirmada com a área responsável.
6. **Meta mal desenhada:** perseguir apenas o número, por exemplo escolhendo quem recebe a pesquisa, melhora o indicador sem melhorar a experiência do cliente.

---

## 3. Análise exploratória: principais respostas

*Detalhes, tabelas e gráficos estão em `notebooks/01_entendimento_e_preparacao.ipynb` (qualidade dos dados) e em `notebooks/02_analise_exploratoria.ipynb`, a EDA (Exploratory Data Analysis, ou análise exploratória de dados).*

### Qualidade e recorte dos dados

A base tem 2.500 pedidos, um por cliente, e passou pelas verificações de qualidade apresentadas na Aula 2: não há valores ausentes nem registros duplicados, e os valores estão dentro de faixas plausíveis. Foram encontradas, porém, duas inconsistências de validade, com 35 pedidos em que o desconto é maior que o valor do pedido e 121 pedidos em que o atraso é maior que o prazo total. Essas linhas somam 6% da base, foram sinalizadas e mantidas, porque a remoção não altera as conclusões e porque a definição das colunas precisa ser confirmada com a área responsável.

Também é importante reconhecer o recorte da realidade que a base representa: ela contém apenas clientes que responderam à pesquisa de NPS e não traz datas, o que impede análises de sazonalidade e de evolução ao longo do tempo.

### Quais fatores parecem mais críticos para a satisfação?

Quatro fatores se destacam, todos com relação negativa com a nota, ou seja, quanto maior o valor, menor a satisfação:

1. **Dias de atraso na entrega**, que é o fator mais forte (correlação de -0,59).
2. **Número de reclamações** (-0,49).
3. **Contatos com o SAC** (-0,34).
4. **Tempo de resolução** (-0,19).

Os demais fatores têm relação praticamente nula com o NPS, entre eles:

- valor do pedido;
- frete e desconto;
- número de parcelas;
- prazo total de entrega;
- idade, região e tempo de relacionamento.

Entre outros.

### O que mais gera detratores?

O atraso de 2 dias ou mais está presente em **72% dos detratores**, e 4 reclamações ou mais aparecem em **70% deles**. Considerando os três fatores críticos em conjunto (atraso de 2 dias ou mais, 4 reclamações ou mais e 2 contatos ou mais com o SAC), **92% dos detratores** passaram por pelo menos um deles, o que indica que a maior parte da detração é evitável pela operação.

### Existe um "ponto de ruptura" na experiência do cliente?

Sim, e ele está em **2 dias de atraso**.

| Atraso | % detratores | NPS |
|---|---|---|
| Sem atraso | 52% | -34 |
| 1 dia | 74% | -67 |
| **2 dias** | **88%** | **-86** |
| 3 dias | 97% | -96 |
| 4 dias ou mais | 99,5% | -99,5 |

A partir de 2 dias de atraso os promotores praticamente desaparecem, caindo para 2%. Nas reclamações há uma ruptura semelhante: com 0 ou 1 reclamação, 28% dos clientes são detratores, e com 2 ou 3 esse percentual sobe para 76%.

Um achado que segue o padrão narrativo de quebra de expectativa, descrito na Aula 4, é que **o prazo total de entrega não altera a satisfação**. Uma entrega de 14 dias que chega na data combinada tem o mesmo NPS que uma entrega de 3 dias, com cerca de 84% de detratores em todas as faixas de prazo. Enquanto o prazo longo é aceito pelo cliente, o atraso em relação ao que foi prometido não é.

Os problemas também se somam: pedidos sem nenhum fator crítico têm NPS de -28, com 1 fator o NPS cai para -77, e com os 3 fatores chega a -97.

### Que tipo de cliente tende a ter NPS mais alto ou mais baixo?

Não foi encontrado um perfil demográfico de detrator. Região, faixa etária, tempo de relacionamento e valor do pedido apresentam diferenças pequenas e sem significância estatística, ou seja, diferenças que podem ser explicadas pelo acaso.

O cliente com NPS mais alto é aquele que **recebeu o pedido no prazo e não precisou reclamar**. Os pedidos sem atraso e com até 1 reclamação formam o único grupo com NPS positivo (+9).

### Registro das hipóteses

Conforme a Aula 1, refutar uma hipótese é tão valioso quanto confirmá-la, e o resultado das hipóteses levantadas no início do trabalho foi o seguinte:

| # | Hipótese | Resultado |
|---|---|---|
| H1 | Atraso na entrega derruba o NPS | Confirmada: é o fator mais forte |
| H2 | Muitos contatos com o SAC e resolução lenta derrubam o NPS | Confirmada |
| H3 | Mais reclamações levam a mais detratores | Confirmada |
| H4 | Frete caro e pouco desconto reduzem a satisfação | Refutada: relação praticamente nula |
| H5 | O perfil do cliente muda o NPS | Refutada: diferenças sem significância estatística |

---

## 4. Estratégia de modelo preditivo

*A implementação completa está em `notebooks/03_modelo_preditivo.ipynb` e na pasta `src/`.*

### Estratégia adotada

| Abordagem | Pergunta respondida | Papel no projeto |
|---|---|---|
| **Classificação** | "Este cliente vai se tornar detrator?" | **Principal**, porque gera uma lista de ação priorizada |
| **Regressão** | "Qual nota este cliente deve dar?" | Comparação e acompanhamento de tendência |

A classificação foi escolhida como abordagem principal por razões de negócio e técnicas. Do ponto de vista do negócio, a operação precisa decidir quem abordar a cada dia, e uma probabilidade de detração, convertida em faixas de risco, leva diretamente a uma ação. Do ponto de vista técnico, o NPS é calculado por categorias, e a regressão erra em média 1,4 ponto na nota, o que é suficiente para trocar a categoria de um cliente que está perto do limite de 7.

### Como o modelo foi construído

| Etapa | Decisão |
|---|---|
| **Variável alvo** | `is_detractor` (nota menor que 7) |
| **Variáveis de entrada** | 14 variáveis de cliente, pedido, logística e atendimento, todas disponíveis antes da pesquisa |
| **Variáveis excluídas** | Identificadores, que não descrevem comportamento, e CSAT e recompra, por vazamento de informação |
| **Preparação** | Padronização das variáveis numéricas e codificação da região, dentro de um pipeline (sequência automatizada de etapas) |
| **Separação dos dados** | 80% para treino e 20% para teste, de forma estratificada, mantendo a mesma proporção de detratores nos dois conjuntos, e validação cruzada de 5 dobras no treino |
| **Modelos comparados** | Baseline (modelo de referência que sempre prevê "detrator"), Regressão Logística, Random Forest (floresta aleatória) e Gradient Boosting (árvores em sequência) |
| **Modelo escolhido** | **Regressão Logística**, que teve desempenho equivalente aos modelos mais complexos e é explicável |
| **Métrica principal** | AUC, porque com 84% de detratores a acurácia (percentual de acertos totais) é enganosa |

### Resultados no conjunto de teste

Os resultados abaixo foram obtidos com dados que o modelo não viu durante o treinamento:

- **AUC de 0,87:** em 87% das vezes, o modelo atribui risco maior a quem de fato se torna detrator.
- **Precisão de 94%:** de cada 100 clientes apontados como detratores, 94 realmente são.
- **Recall (sensibilidade) de 83%:** o modelo encontra 83% dos detratores antes da pesquisa.

| Faixa de risco | % real de detratores | Ação sugerida |
|---|---|---|
| Alto (probabilidade ≥ 90%) | **100%** | Ligação em até 24 horas e compensação |
| Médio (60% a 90%) | 91% | Mensagem proativa e canal prioritário |
| Baixo (abaixo de 60%) | 61% | Jornada padrão, com monitoramento |

O modelo de regressão, usado como comparação, teve MAE (Mean Absolute Error, ou erro absoluto médio) de 1,4 ponto, contra 2,0 de um modelo que sempre prevê a média, e R² (coeficiente de determinação) de 0,52, o que significa que ele explica cerca de 52% da variação das notas.

### Como a empresa poderia usar a solução na prática

1. Todos os dias, o modelo calcula o risco dos pedidos em andamento com os dados de logística e de atendimento.
2. A lista de clientes de alto risco é enviada à área de Experiência do Cliente para contato proativo.
3. A Logística recebe um painel com os pedidos em risco por transportadora e por rota.
4. A liderança acompanha o NPS projetado antes da aplicação da pesquisa.
5. Todos os meses, o resultado previsto é comparado com o real, e o modelo é retreinado se o desempenho cair.

### Impacto estimado

Uma simulação feita com os próprios dados históricos estimou o NPS em diferentes cenários:

| Cenário | NPS estimado | Ganho |
|---|---|---|
| Situação atual | -80 | — |
| Atraso máximo de 1 dia | -66 | +14 |
| Nenhum atraso | -53 | +27 |
| **Atraso máximo de 1 dia e até 3 reclamações** | **-41** | **+39** |

> Essas estimativas se baseiam em correlações observadas na base e não comprovam relação de causa, por isso precisam ser confirmadas com um piloto antes de qualquer decisão em larga escala.

---

## 5. Recomendações priorizadas

Seguindo a Aula 4, as recomendações abaixo são desdobramentos das evidências apresentadas, e incluem também as ações de aprofundamento e validação que a análise ainda exige.

| Prioridade | Ação | Área | Indicador de acompanhamento |
|---|---|---|---|
| 1 | **Alerta de atraso:** acionar um plano de contingência quando o pedido se aproximar de 1 dia de atraso | Logística | % de pedidos com 2 dias de atraso ou mais |
| 2 | **Prazo realista:** recalibrar o prazo exibido no checkout (etapa final da compra) por rota, com base no histórico | Logística / Produto | % de entregas no prazo prometido |
| 3 | **Contato proativo:** avisar o cliente antes que ele precise reclamar e oferecer compensação | Experiência do Cliente | NPS dos pedidos atrasados |
| 4 | **Resolução no primeiro contato:** dar autonomia ao SAC e criar fila prioritária a partir do segundo contato | Atendimento | FCR e tempo médio de resolução |
| 5 | **Origem das reclamações:** classificar os motivos (produto, seller, embalagem, entre outros) e atacar os principais | Produto / Marketplace | Reclamações por pedido |
| 6 | **Modelo em produção com piloto:** pontuar o risco diariamente e medir o efeito com um teste A/B (comparação entre um grupo que recebe a mudança e outro que não recebe) | Dados / Experiência do Cliente | Diferença de NPS entre o grupo piloto e o grupo de controle |
| 7 | **Aprofundar a análise:** confirmar a definição das colunas de prazo e atraso, e incluir dados de transportadora, categoria de produto e motivo da reclamação | Dados | Base enriquecida e validada |

---

## 6. Limitações e riscos

- **Correlação não é causa:** os resultados mostram associações, e cada ação precisa ser validada com piloto ou teste A/B antes de ser ampliada.
- **Indícios de base simulada:** alguns padrões são muito regulares, como a recompra de 0% entre detratores e de 100% entre promotores, e em dados reais é esperado um desempenho menor do modelo.
- **Ausência de datas:** não é possível analisar sazonalidade, tendência ou o momento exato de cada evento da jornada.
- **Inconsistências:** 6% das linhas têm combinações improváveis, que foram sinalizadas e não alteram as conclusões.
- **Recorte da base:** a base contém apenas clientes que responderam à pesquisa, o que pode não representar toda a base de clientes.
- **Variáveis ausentes:** motivo da reclamação, transportadora, categoria do produto e canal de venda enriqueceriam a análise.
- **Uso ético:** o risco previsto deve ser usado para ajudar o cliente, e nunca para tratá-lo de forma pior ou para punir colaboradores.

---

## Referências

Bibliografia das aulas da Fase 1 que fundamentou a metodologia deste trabalho:

- DUARTE, N. *DataStory: explique dados e inspire ações por meio de histórias*. Rio de Janeiro: Alta Books, 2021.
- GRUS, J. *Data Science do zero: noções fundamentais com Python*. 2. ed. Rio de Janeiro: Alta Books, 2021.
- KNAFLIC, C. N. *Storytelling com dados: um guia sobre visualização de dados para profissionais de negócios*. Rio de Janeiro: Alta Books, 2019.
- PROVOST, F.; FAWCETT, T. *Data Science para negócios*. Rio de Janeiro: Alta Books, 2016.

---

## Glossário

| Termo | Significado |
|---|---|
| A/B (teste A/B) | Comparação entre um grupo que recebe uma mudança e outro que não recebe, para medir o efeito da mudança. |
| ABT (And–But–Therefore) | Estrutura de narrativa em três partes: situação, conflito e consequência. |
| Acurácia | Percentual de acertos totais do modelo; nesta base é enganosa, porque prever "detrator" para todos já acerta 84%. |
| AUC (Area Under the Curve) | Mede se o modelo ordena bem os clientes por risco; 0,5 equivale ao acaso e 1,0 a acerto perfeito. |
| Baseline | Modelo de referência mais simples possível, usado para verificar se o modelo real aprendeu algo. |
| Benchmark | Valor de referência do mercado usado para comparação. |
| CAC (Custo de Aquisição de Cliente) | Valor gasto pela empresa para conquistar um cliente novo. |
| Checkout | Etapa final da compra, em que o prazo de entrega é informado ao cliente. |
| Churn | Taxa de clientes que deixam de comprar da empresa. |
| Classificação | Tipo de modelo que prevê uma categoria, como detrator ou não detrator. |
| CRM (Customer Relationship Management) | Gestão do relacionamento com o cliente, incluindo histórico, segmentação e campanhas. |
| CSAT (Customer Satisfaction Score) | Nota de satisfação do cliente com uma interação específica. |
| Detrator | Cliente que deu nota de 0 a 6 e tende a não recomendar a empresa. |
| EDA (Exploratory Data Analysis) | Análise exploratória de dados, etapa de investigação da qualidade, da distribuição e das relações entre variáveis. |
| Estratificação | Separação dos dados que mantém a mesma proporção de cada classe nos conjuntos de treino e teste. |
| FCR (First Contact Resolution) | Percentual de problemas resolvidos no primeiro contato com o atendimento. |
| Gradient Boosting | Modelo que combina várias árvores de decisão em sequência, em que cada uma corrige os erros da anterior. |
| LTV (Lifetime Value) | Receita gerada por um cliente durante todo o relacionamento com a empresa. |
| MAE (Mean Absolute Error) | Erro médio do modelo de regressão, medido na mesma unidade da nota. |
| Market share | Participação da empresa no mercado em que atua. |
| Neutro | Cliente que deu nota 7 ou 8; está satisfeito, mas não chega a recomendar a empresa. |
| NPS (Net Promoter Score) | Percentual de promotores menos o percentual de detratores; varia de -100 a +100. |
| Pipeline | Sequência automatizada de etapas de preparação dos dados e de modelagem. |
| Ponto de ruptura | Limite a partir do qual a satisfação cai de forma acentuada; nesta análise, 2 dias de atraso. |
| Precisão | Percentual de clientes apontados como detratores que realmente são detratores. |
| Pricing | Definição de preços, descontos e frete. |
| Promotor | Cliente que deu nota 9 ou 10 e tende a recomendar a empresa. |
| R² (coeficiente de determinação) | Proporção da variação das notas que o modelo de regressão consegue explicar, de 0 a 1. |
| Random Forest | Modelo que combina muitas árvores de decisão independentes e usa a votação entre elas. |
| Recall (sensibilidade) | Percentual de detratores reais que o modelo conseguiu identificar. |
| Regressão | Tipo de modelo que prevê um número, como a nota de 0 a 10. |
| Regressão Logística | Modelo de classificação que calcula uma probabilidade e mostra o peso de cada variável. |
| SAC (Serviço de Atendimento ao Consumidor) | Canal de atendimento ao cliente. |
| Seller | Vendedor parceiro que vende produtos por meio do marketplace. |
| Share of search | Participação da marca nas buscas feitas na internet dentro do seu mercado. |
| Significância estatística | Indicação de que uma diferença observada dificilmente é fruto do acaso. |
| SLA (Service Level Agreement) | Prazo ou padrão de serviço combinado, como resolver um problema em até 2 dias. |
| Target (variável alvo) | Variável que o modelo procura prever. |
| Validação cruzada | Técnica que testa o modelo várias vezes em partes diferentes dos dados de treino. |
| Vazamento de informação (*data leakage*) | Uso, no modelo, de um dado que só existe depois do resultado, o que infla o desempenho. |
