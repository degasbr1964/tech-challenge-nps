# NPS Preditivo: fatores que levam o cliente à detração

**Tech Challenge · Fase 1 · Pós-graduação AI Scientist**

**Integrante:** Edgar Takakura — RM 371998

Este projeto analisa 2.500 pedidos de um e-commerce com dois objetivos: identificar quais fatores operacionais explicam o NPS (Net Promoter Score, ou índice de recomendação do cliente) e construir um modelo que aponte, antes da aplicação da pesquisa, os clientes com maior risco de se tornarem detratores.

---

## 1. Objetivo do projeto

Hoje o NPS da empresa só é coletado depois do encerramento da jornada de compra, quando o cliente já formou sua opinião e não há mais como agir de forma preventiva. Para mudar esse cenário, o trabalho parte de uma pergunta de análise e de uma pergunta para o modelo.

Pergunta da análise:

> **Quais fatores operacionais de pedido, logística e atendimento explicam por que um cliente se torna detrator?**

Pergunta do modelo preditivo (desafio opcional):

> **Com os dados do pedido disponíveis antes da pesquisa, qual a chance de este cliente se tornar detrator?**

## 2. Principais resultados

| Tema | Resultado |
|---|---|
| **NPS atual** | **-80**, com 84% de detratores, 11% de neutros e 4% de promotores |
| **Fator principal** | **Atraso na entrega**, em que cada dia de atraso reduz a nota média em cerca de 1 ponto |
| **Ponto de ruptura** | **2 dias de atraso**, faixa em que 88% dos clientes são detratores e onde estão 64% dos pedidos |
| **Prazo x atraso** | O prazo total de entrega, de 2 a 14 dias, não altera o NPS, enquanto o atraso altera |
| **Atendimento** | 2 reclamações ou mais e 2 contatos ou mais com o SAC (Serviço de Atendimento ao Consumidor) elevam a detração |
| **Perfil do cliente** | Região, idade, tempo de relacionamento e valor do pedido não apresentam diferença relevante |
| **Efeito combinado** | Pedidos sem fator crítico têm NPS de -28, e pedidos com 3 fatores críticos têm NPS de -97 |
| **Modelo** | Regressão Logística com AUC (Area Under the Curve, ou área sob a curva) de 0,87 e precisão de 94%; na faixa de alto risco, 100% dos clientes foram detratores |
| **Simulação** | Atraso máximo de 1 dia e até 3 reclamações levariam o NPS estimado a **-41**, um ganho de 39 pontos |

## 3. Recomendações

Cinco ações priorizadas a partir das evidências, na mesma ordem levada à apresentação gerencial:

| # | Ação | Área | Como medir |
|---|---|---|---|
| 1 | **Alerta de atraso:** plano de contingência quando o pedido se aproxima de 1 dia de atraso | Logística | % de pedidos com 2 dias de atraso ou mais |
| 2 | **Prazo realista no checkout (etapa final da compra):** recalibrar a promessa por rota, com base no histórico real | Logística / Produto | % de entregas no prazo prometido |
| 3 | **Contato proativo:** avisar o cliente antes que ele reclame e compensar os casos de alto risco | Experiência do Cliente | NPS dos pedidos atrasados |
| 4 | **Resolução no 1º contato:** autonomia ao SAC, fila prioritária no 2º contato e SLA (Service Level Agreement, ou acordo de nível de serviço) de até 2 dias | Atendimento | % de resolução no 1º contato |
| 5 | **Modelo em produção com piloto:** pontuação diária de risco e teste A/B (comparação entre um grupo que recebe a mudança e outro que não recebe) para medir o ganho real | Dados | NPS do piloto contra o grupo de controle |

## 4. Estrutura do repositório

```
tech-challenge-nps/
├── data/
│   ├── raw/                      # base original, sem alterações
│   │   └── desafio_nps_fase_1.csv
│   └── processed/                # arquivos gerados pelos notebooks e scripts
│       ├── nps_tratado.csv       # base com target, sinalizações e faixas de análise
│       └── pedidos_com_risco.csv # pedidos pontuados pelo modelo
├── notebooks/
│   ├── 01_entendimento_e_preparacao.ipynb  # qualidade dos dados, tratamento, target e vazamento
│   ├── 02_analise_exploratoria.ipynb       # EDA (análise exploratória) com foco em negócio
│   └── 03_modelo_preditivo.ipynb           # classificação, regressão e simulação de cenários
├── src/
│   ├── config.py           # caminhos, colunas, regras de negócio e cores
│   ├── data_prep.py        # carga, validação e preparação da base
│   ├── viz.py              # funções de gráfico padronizadas
│   ├── train_model.py      # treino, comparação e avaliação dos modelos
│   ├── predict.py          # pontuação de novos pedidos
│   └── run_notebook.py     # execução dos notebooks pela linha de comando
├── models/                 # modelos treinados (.joblib)
├── reports/
│   ├── figures/            # gráficos gerados (PNG)
│   ├── metricas_modelo.json
│   └── relatorio_negocio.md# respostas aos itens 1 a 4 do enunciado
├── docs/                   # apresentação gerencial e roteiro do vídeo
├── requirements.txt
└── README.md
```

## 5. Descrição da base de dados

O arquivo `data/raw/desafio_nps_fase_1.csv` tem **2.500 pedidos**, um por cliente, e 19 colunas, sem valores ausentes e sem registros duplicados.

| Bloco | Coluna | Descrição | Tipo de variável |
|---|---|---|---|
| Identificação | `customer_id`, `order_id` | Identificadores únicos | Identificador |
| Cliente | `customer_age` | Idade (18 a 69 anos) | Numérica discreta |
| | `customer_region` | Região (Norte, Nordeste, Centro-Oeste, Sudeste e Sul) | Categórica nominal |
| | `customer_tenure_months` | Tempo de relacionamento, em meses | Numérica discreta |
| Pedido | `order_value` | Valor total do pedido (R$) | Numérica contínua |
| | `items_quantity` | Quantidade de itens | Numérica discreta |
| | `discount_value` | Desconto aplicado (R$) | Numérica contínua |
| | `payment_installments` | Número de parcelas | Numérica discreta |
| Logística | `delivery_time_days` | Prazo total de entrega, em dias | Numérica discreta |
| | `delivery_delay_days` | Dias de atraso | Numérica discreta |
| | `freight_value` | Valor do frete (R$) | Numérica contínua |
| | `delivery_attempts` | Tentativas de entrega | Numérica discreta |
| Atendimento | `customer_service_contacts` | Contatos com o SAC | Numérica discreta |
| | `resolution_time_days` | Tempo para resolver problemas, em dias | Numérica discreta |
| | `complaints_count` | Reclamações registradas | Numérica discreta |
| Pós-jornada | `repeat_purchase_30d` | Recompra em até 30 dias (0 ou 1) | Booleana |
| | `csat_internal_score` | CSAT (Customer Satisfaction Score, ou índice de satisfação do cliente) interno, de 0 a 10 | Numérica contínua |
| **Alvo** | `nps_score` | Nota NPS, de 0 a 10, coletada após a experiência de compra | Numérica contínua |

**Pontos de atenção encontrados na base:**

- Há 35 pedidos com desconto maior que o valor do pedido e 121 com atraso maior que o prazo total, que somam 6% da base. Essas linhas foram sinalizadas e mantidas, porque a remoção não altera as conclusões.
- A coluna `nps_score` tem casas decimais, e por isso foi adotada a regra Detrator para notas menores que 7, Neutro de 7 a menos de 9 e Promotor para 9 ou mais.
- As colunas `csat_internal_score` e `repeat_purchase_30d` são medidas junto com o NPS ou depois dele, e ficaram fora do modelo para evitar vazamento de informação (*data leakage*).

## 6. Metodologia

A metodologia segue o fluxo apresentado nas aulas da Fase 1: perguntar, explorar, visualizar e comunicar.

1. **Entendimento do negócio e perguntas analíticas (Aula 1).** A pergunta orientadora foi decomposta em hipóteses testáveis (H1 a H5) e classificada nos quatro níveis de pergunta: descritiva, diagnóstica, preditiva e prescritiva.
2. **Qualidade e preparação dos dados (Aula 2).** A base foi verificada quanto a completude, consistência, validade, precisão e atualidade, com uso de `info()`, `isnull()`, `duplicated()` e `describe()`. Os outliers (valores extremos) foram mantidos, porque representam casos reais, e cada decisão de tratamento foi documentada.
3. **EDA (Exploratory Data Analysis, ou análise exploratória de dados) e visualização (Aulas 2 e 3).** Foram usados histogramas para distribuição, gráficos de barras e boxplots para comparação entre grupos, heatmap de correlação e correlação de Spearman (que mede se duas variáveis variam juntas) para relações, e barras empilhadas para composição. As diferenças entre perfis foram testadas com o teste de Kruskal-Wallis (que verifica se grupos têm notas realmente diferentes), e cada descoberta foi registrada no formato Observação → Evidência → Hipótese → Próximos passos.
4. **Modelagem preditiva (desafio opcional).**
   - O alvo principal é `is_detractor` (nota menor que 7), tratado como problema de **classificação**, e a regressão da nota de 0 a 10 foi usada como comparação.
   - As entradas são 14 variáveis disponíveis antes da pesquisa, sem identificadores e sem variáveis de vazamento.
   - Os dados foram separados em 80% para treino e 20% para teste, de forma estratificada (mantendo a mesma proporção de detratores), com validação cruzada de 5 dobras no treino e uso do teste uma única vez.
   - Foram comparados um baseline (modelo de referência), a Regressão Logística, o Random Forest (floresta aleatória) e o Gradient Boosting (árvores em sequência), e a **Regressão Logística** foi escolhida por ter desempenho equivalente e ser explicável.
   - A métrica principal é a AUC, porque a acurácia é enganosa com 84% de detratores, e também foram avaliados precisão, recall (sensibilidade) e F1 (equilíbrio entre precisão e recall). Na regressão, foram usados o MAE (Mean Absolute Error, ou erro absoluto médio) e o R² (coeficiente de determinação).
5. **Storytelling e recomendações (Aula 4).** Os resultados foram organizados nos frameworks ABT (And–But–Therefore) e Pergunta → Descoberta → Insight → Recomendação, com faixas de risco, uma ação por faixa e simulação de cenários.

## 7. Como reproduzir os resultados

É necessário ter o Python 3.10 ou superior instalado.

```bash
# 1. Clonar o repositório e entrar na pasta do projeto
git clone <url-do-repositorio>
cd tech-challenge-nps

# 2. Criar o ambiente virtual e instalar as dependências
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3a. Executar pelo Jupyter (recomendado para leitura)
jupyter notebook notebooks/
#    Execute os notebooks na ordem: 01 → 02 → 03

# 3b. Ou executar tudo pela linha de comando
python -m src.data_prep            # gera data/processed/nps_tratado.csv
python -m src.train_model          # treina, avalia e salva os modelos
python -m src.predict              # pontua os pedidos e gera a lista de risco
python -m src.run_notebook notebooks/01_entendimento_e_preparacao.ipynb \
    notebooks/02_analise_exploratoria.ipynb notebooks/03_modelo_preditivo.ipynb
```

Todos os resultados usam `random_state=42` (semente fixa) e podem ser reproduzidos.

Para pontuar novos pedidos, basta informar o arquivo, que precisa ter as mesmas colunas operacionais da base original e não precisa conter a nota NPS:

```bash
python -m src.predict caminho/novos_pedidos.csv
```

## 8. Limitações

- **Correlação não é causa:** as recomendações devem ser validadas com piloto ou teste A/B (comparação entre um grupo que recebe a mudança e outro que não recebe).
- **Indícios de base simulada:** há relações muito regulares, como a recompra de 0% entre detratores e de 100% entre promotores, e em dados reais o desempenho tende a ser menor.
- **Ausência de datas:** não é possível analisar sazonalidade nem evolução ao longo do tempo.
- **Recorte da base:** a base contém apenas clientes que responderam à pesquisa.
- **Definições a confirmar:** a relação entre `delivery_time_days` e `delivery_delay_days` e o motivo de a nota NPS ter casas decimais.

## 9. Entregáveis

- Notebooks e código: este repositório
- Relatório de negócio: [`reports/relatorio_negocio.md`](reports/relatorio_negocio.md)
- Apresentação gerencial: [`docs/apresentacao_gerencial_nps.pptx`](docs/apresentacao_gerencial_nps.pptx)
- Vídeo executivo: [`docs/apresentacao_gerencial_nps.mp4`](docs/apresentacao_gerencial_nps.mp4)
- Roteiro da apresentação: [`docs/Roteiro_apresentacao_NPS.md`](docs/Roteiro_apresentacao_NPS.md)

## 10. Referências

- DUARTE, N. *DataStory: explique dados e inspire ações por meio de histórias*. Rio de Janeiro: Alta Books, 2021.
- GRUS, J. *Data Science do zero: noções fundamentais com Python*. 2. ed. Rio de Janeiro: Alta Books, 2021.
- KNAFLIC, C. N. *Storytelling com dados: um guia sobre visualização de dados para profissionais de negócios*. Rio de Janeiro: Alta Books, 2019.
- PROVOST, F.; FAWCETT, T. *Data Science para negócios*. Rio de Janeiro: Alta Books, 2016.

---

## Glossário

| Termo | Significado |
|---|---|
| A/B (teste A/B) | Comparação entre um grupo que recebe uma mudança e outro que não recebe. |
| ABT (And–But–Therefore) | Estrutura de narrativa em três partes: situação, conflito e consequência. |
| Acurácia | Percentual de acertos totais do modelo; nesta base é enganosa, porque prever "detrator" para todos já acerta 84%. |
| AUC (Area Under the Curve) | Mede se o modelo ordena bem os clientes por risco; 0,5 equivale ao acaso e 1,0 a acerto perfeito. |
| Baseline | Modelo de referência mais simples possível, usado para verificar se o modelo real aprendeu algo. |
| Boxplot | Gráfico que mostra mediana, quartis e valores extremos de uma variável. |
| Checkout | Etapa final da compra, em que o prazo de entrega é informado ao cliente. |
| Classificação | Tipo de modelo que prevê uma categoria, como detrator ou não detrator. |
| CSAT (Customer Satisfaction Score) | Nota de satisfação do cliente com uma interação específica. |
| Detrator | Cliente que deu nota de 0 a 6 e tende a não recomendar a empresa. |
| EDA (Exploratory Data Analysis) | Análise exploratória de dados. |
| Estratificação | Separação dos dados que mantém a mesma proporção de cada classe em treino e teste. |
| F1 | Medida que equilibra precisão e recall. |
| Gradient Boosting | Modelo que combina árvores de decisão em sequência, em que cada uma corrige a anterior. |
| Heatmap de correlação | Tabela colorida que mostra a correlação entre pares de variáveis. |
| Histograma | Gráfico que mostra como os valores de uma variável se distribuem em faixas. |
| Kruskal-Wallis | Teste estatístico que verifica se vários grupos têm notas realmente diferentes. |
| MAE (Mean Absolute Error) | Erro médio do modelo de regressão, na mesma unidade da nota. |
| Neutro | Cliente que deu nota 7 ou 8. |
| NPS (Net Promoter Score) | Percentual de promotores menos o percentual de detratores; varia de -100 a +100. |
| Outlier | Valor muito distante do padrão da variável, que nem sempre é um erro. |
| Precisão | Percentual de clientes apontados como detratores que realmente são detratores. |
| Promotor | Cliente que deu nota 9 ou 10. |
| R² (coeficiente de determinação) | Proporção da variação das notas que o modelo explica, de 0 a 1. |
| Random Forest | Modelo que combina muitas árvores de decisão independentes e usa a votação entre elas. |
| random_state | Semente fixa que garante os mesmos resultados a cada execução. |
| Recall (sensibilidade) | Percentual de detratores reais que o modelo conseguiu identificar. |
| Regressão | Tipo de modelo que prevê um número, como a nota de 0 a 10. |
| Regressão Logística | Modelo de classificação que calcula uma probabilidade e mostra o peso de cada variável. |
| SAC (Serviço de Atendimento ao Consumidor) | Canal de atendimento ao cliente. |
| Spearman (correlação de) | Medida, de -1 a +1, que indica se duas variáveis aumentam ou diminuem juntas. |
| Target (variável alvo) | Variável que o modelo procura prever. |
| Validação cruzada | Técnica que testa o modelo várias vezes em partes diferentes dos dados de treino. |
| Vazamento de informação (*data leakage*) | Uso, no modelo, de um dado que só existe depois do resultado, o que infla o desempenho. |
