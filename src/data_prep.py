"""
Carga, validação e preparação da base de NPS.

Uso pela linha de comando:
    python -m src.data_prep
Gera o arquivo data/processed/nps_tratado.csv.
"""
import pandas as pd

from src import config


def load_raw_data(path=config.RAW_DATA_PATH) -> pd.DataFrame:
    """Lê o CSV original sem nenhuma alteração."""
    return pd.read_csv(path)


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resume a qualidade de cada coluna: tipo, nulos, valores únicos,
    mínimo e máximo. Serve para documentar que a base foi checada.
    """
    report = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "valores_unicos": df.nunique(),
        "minimo": df.min(numeric_only=True),
        "maximo": df.max(numeric_only=True),
    })
    return report.reindex(df.columns)


def validate_business_rules(df: pd.DataFrame) -> dict:
    """
    Confere regras que precisam ser verdadeiras para os dados fazerem sentido.
    Retorna a quantidade de linhas que VIOLAM cada regra (o ideal é zero).
    """
    checks = {
        "linhas_duplicadas": int(df.duplicated().sum()),
        "pedidos_duplicados": int(df["order_id"].duplicated().sum()),
        "nps_fora_de_0_a_10": int((~df["nps_score"].between(0, 10)).sum()),
        "csat_fora_de_0_a_10": int((~df["csat_internal_score"].between(0, 10)).sum()),
        "idade_fora_de_18_a_100": int((~df["customer_age"].between(18, 100)).sum()),
        "valores_negativos": int((df.select_dtypes("number") < 0).any(axis=1).sum()),
        "desconto_maior_que_pedido": int((df["discount_value"] > df["order_value"]).sum()),
        "atraso_maior_que_prazo_total": int((df["delivery_delay_days"] > df["delivery_time_days"]).sum()),
        "recompra_diferente_de_0_ou_1": int((~df["repeat_purchase_30d"].isin([0, 1])).sum()),
    }
    return checks


def classify_nps(score: float) -> str:
    """Aplica a regra padrão do NPS a uma nota individual."""
    if score < config.DETRACTOR_THRESHOLD:
        return "Detrator"
    if score < config.PROMOTER_THRESHOLD:
        return "Neutro"
    return "Promotor"


def calculate_nps(scores: pd.Series) -> float:
    """
    NPS = % promotores - % detratores. Varia de -100 a +100.
    """
    categories = scores.apply(classify_nps)
    share = categories.value_counts(normalize=True)
    return 100 * (share.get("Promotor", 0) - share.get("Detrator", 0))


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a categoria NPS e o alvo binário de classificação."""
    df = df.copy()
    df[config.NPS_CATEGORY] = df[config.TARGET_SCORE].apply(classify_nps)
    df[config.TARGET_CLASS] = (df[config.TARGET_SCORE] < config.DETRACTOR_THRESHOLD).astype(int)
    return df


def add_analysis_bands(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria faixas legíveis para a análise exploratória (não entram no modelo).
    Faixas facilitam a leitura por gestores: "atraso de 2 a 3 dias" é mais
    claro que um coeficiente de correlação.
    """
    df = df.copy()
    df["faixa_atraso"] = pd.cut(
        df["delivery_delay_days"], bins=[-1, 0, 1, 2, 3, 99],
        labels=["Sem atraso", "1 dia", "2 dias", "3 dias", "4+ dias"],
    )
    df["faixa_reclamacoes"] = pd.cut(
        df["complaints_count"], bins=[-1, 1, 3, 5, 99],
        labels=["0-1", "2-3", "4-5", "6+"],
    )
    df["faixa_contatos_sac"] = pd.cut(
        df["customer_service_contacts"], bins=[-1, 0, 1, 2, 3, 99],
        labels=["0", "1", "2", "3", "4+"],
    )
    df["faixa_resolucao"] = pd.cut(
        df["resolution_time_days"], bins=[-1, 2, 5, 8, 99],
        labels=["0-2 dias", "3-5 dias", "6-8 dias", "9+ dias"],
    )
    df["faixa_idade"] = pd.cut(
        df["customer_age"], bins=[17, 25, 35, 45, 55, 120],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )
    df["faixa_tempo_casa"] = pd.cut(
        df["customer_tenure_months"], bins=[0, 12, 36, 60, 90, 999],
        labels=["Até 1 ano", "1-3 anos", "3-5 anos", "5-7,5 anos", "7,5+ anos"],
    )
    df["faixa_valor_pedido"] = pd.qcut(
        df["order_value"], q=4, labels=["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"],
    )
    return df


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de preparação usado pelos notebooks e scripts."""
    df = df.drop_duplicates().copy()
    df["customer_region"] = df["customer_region"].str.strip()
    # Sinaliza (sem remover) linhas com inconsistências lógicas.
    # Decisão documentada no notebook 01: são 6% da base e não mudam as
    # conclusões; removê-las sem confirmar com a área de dados seria arbitrário.
    df["flag_desconto_maior_que_pedido"] = (df["discount_value"] > df["order_value"]).astype(int)
    df["flag_atraso_maior_que_prazo"] = (df["delivery_delay_days"] > df["delivery_time_days"]).astype(int)
    df = add_targets(df)
    df = add_analysis_bands(df)
    return df


if __name__ == "__main__":
    raw = load_raw_data()
    print("Regras violadas:", validate_business_rules(raw))
    prepared = prepare_dataset(raw)
    config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(config.PROCESSED_DATA_PATH, index=False)
    print(f"Base tratada salva em {config.PROCESSED_DATA_PATH} ({len(prepared)} linhas)")
