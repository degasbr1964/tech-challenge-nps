"""
Configurações centrais do projeto.

Concentra caminhos, nomes de colunas e parâmetros usados em todos os
notebooks e scripts. Assim, qualquer ajuste é feito em um único lugar.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "desafio_nps_fase_1.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / "nps_tratado.csv"
SCORED_DATA_PATH = ROOT_DIR / "data" / "processed" / "pedidos_com_risco.csv"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

CLASSIFIER_PATH = MODELS_DIR / "modelo_classificacao_detrator.joblib"
REGRESSOR_PATH = MODELS_DIR / "modelo_regressao_nps.joblib"
METRICS_PATH = REPORTS_DIR / "metricas_modelo.json"

# ---------------------------------------------------------------------------
# Reprodutibilidade
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.20

# ---------------------------------------------------------------------------
# Regras de negócio do NPS
# ---------------------------------------------------------------------------
# A base traz notas com casas decimais (ex.: 6.9). Aplicamos a regra padrão
# do NPS usando limites contínuos:
#   Detrator: nota < 7  |  Neutro: 7 <= nota < 9  |  Promotor: nota >= 9
DETRACTOR_THRESHOLD = 7.0
PROMOTER_THRESHOLD = 9.0

TARGET_SCORE = "nps_score"          # alvo da regressão (nota contínua 0-10)
TARGET_CLASS = "is_detractor"       # alvo da classificação (1 = detrator)
NPS_CATEGORY = "nps_category"       # rótulo Detrator / Neutro / Promotor

# ---------------------------------------------------------------------------
# Grupos de variáveis
# ---------------------------------------------------------------------------
ID_COLUMNS = ["customer_id", "order_id"]

CUSTOMER_FEATURES = ["customer_age", "customer_region", "customer_tenure_months"]
ORDER_FEATURES = ["order_value", "items_quantity", "discount_value", "payment_installments"]
LOGISTICS_FEATURES = ["delivery_time_days", "delivery_delay_days", "freight_value", "delivery_attempts"]
SERVICE_FEATURES = ["customer_service_contacts", "resolution_time_days", "complaints_count"]

# Variáveis que só existem DEPOIS (ou junto) da pesquisa de NPS.
# Usá-las no modelo seria "colar a resposta": vazamento de informação.
LEAKAGE_COLUMNS = ["csat_internal_score", "repeat_purchase_30d"]

CATEGORICAL_FEATURES = ["customer_region"]
NUMERIC_FEATURES = [
    "customer_age",
    "customer_tenure_months",
    *ORDER_FEATURES,
    *LOGISTICS_FEATURES,
    *SERVICE_FEATURES,
]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Nomes amigáveis para gráficos e relatórios (público não técnico)
FRIENDLY_NAMES = {
    "customer_age": "Idade do cliente",
    "customer_region": "Região",
    "customer_tenure_months": "Tempo de casa (meses)",
    "order_value": "Valor do pedido",
    "items_quantity": "Qtd. de itens",
    "discount_value": "Desconto",
    "payment_installments": "Parcelas",
    "delivery_time_days": "Prazo total de entrega",
    "delivery_delay_days": "Dias de atraso",
    "freight_value": "Valor do frete",
    "delivery_attempts": "Tentativas de entrega",
    "customer_service_contacts": "Contatos com o SAC",
    "resolution_time_days": "Tempo de resolução",
    "complaints_count": "Reclamações",
    "csat_internal_score": "CSAT interno",
    "repeat_purchase_30d": "Recompra em 30 dias",
    "nps_score": "Nota NPS",
}

# ---------------------------------------------------------------------------
# Paleta de cores (validada para daltonismo)
# ---------------------------------------------------------------------------
COLOR_DETRACTOR = "#e34948"   # vermelho  -> detrator / alerta
COLOR_PASSIVE = "#b5b3ab"     # cinza     -> neutro
COLOR_PROMOTER = "#2a78d6"    # azul      -> promotor / destaque positivo
COLOR_MAIN = "#2a78d6"        # cor principal de séries únicas
COLOR_CONTEXT = "#c3c2b7"     # cor de contexto (barras sem destaque)
COLOR_TEXT = "#0b0b0b"
COLOR_TEXT_SECONDARY = "#52514e"
COLOR_GRID = "#e1e0d9"
CATEGORY_COLORS = {"Detrator": COLOR_DETRACTOR, "Neutro": COLOR_PASSIVE, "Promotor": COLOR_PROMOTER}
