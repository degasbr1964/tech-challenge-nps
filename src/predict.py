"""
Uso prático do modelo: pontuar pedidos ANTES da pesquisa de NPS.

Recebe um CSV com as mesmas colunas operacionais da base (sem a nota) e
devolve, para cada pedido, a probabilidade de detração, a faixa de risco,
a nota estimada e a ação sugerida.

Uso:
    python -m src.predict                          # pontua a própria base
    python -m src.predict caminho/novos_pedidos.csv
"""
import sys

import joblib
import pandas as pd

from src import config
from src.train_model import risk_band

SUGGESTED_ACTION = {
    "Alto": "Contato proativo em até 24h + compensação (cupom/frete grátis)",
    "Médio": "Mensagem proativa com status da entrega e canal prioritário",
    "Baixo": "Jornada padrão; monitorar",
}


def main_driver(row: pd.Series) -> str:
    """Regra simples para indicar o principal motivo de risco do pedido."""
    if row["delivery_delay_days"] >= 2:
        return "Atraso na entrega"
    if row["complaints_count"] >= 4:
        return "Histórico de reclamações"
    if row["customer_service_contacts"] >= 2 or row["resolution_time_days"] >= 9:
        return "Atendimento (muitos contatos / resolução lenta)"
    return "Sem fator crítico"


def score_orders(orders: pd.DataFrame) -> pd.DataFrame:
    classifier = joblib.load(config.CLASSIFIER_PATH)
    regressor = joblib.load(config.REGRESSOR_PATH)
    features = orders[config.MODEL_FEATURES]

    result = orders[["customer_id", "order_id"]].copy()
    result["prob_detrator"] = classifier.predict_proba(features)[:, 1].round(3)
    result["faixa_risco"] = risk_band(result["prob_detrator"]).values
    result["nota_estimada"] = regressor.predict(features).clip(0, 10).round(1)
    result["principal_motivo"] = orders.apply(main_driver, axis=1)
    result["acao_sugerida"] = result["faixa_risco"].astype(str).map(SUGGESTED_ACTION)
    return result.sort_values("prob_detrator", ascending=False)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else config.RAW_DATA_PATH
    scored = score_orders(pd.read_csv(path))
    scored.to_csv(config.SCORED_DATA_PATH, index=False)
    print(scored["faixa_risco"].value_counts().sort_index())
    print(f"\nArquivo salvo em {config.SCORED_DATA_PATH}")
    print(scored.head(10).to_string(index=False))
