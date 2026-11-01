"""
Treino e avaliação dos modelos preditivos de NPS.

Duas abordagens, como pede o desafio:
  1. Classificação (principal): o cliente vai ser DETRATOR (nota < 7)?
  2. Regressão (comparação):   qual nota de 0 a 10 o cliente deve dar?

Uso pela linha de comando:
    python -m src.train_model
Salva os modelos em models/ e as métricas em reports/metricas_modelo.json.
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    average_precision_score, confusion_matrix, f1_score, mean_absolute_error,
    precision_score, r2_score, recall_score, roc_auc_score, root_mean_squared_error,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import config
from src.data_prep import load_raw_data, prepare_dataset

# Faixas de risco usadas na operação (probabilidade de ser detrator)
RISK_BINS = [0, 0.60, 0.90, 1.0001]
RISK_LABELS = ["Baixo", "Médio", "Alto"]


def build_preprocessor() -> ColumnTransformer:
    """
    Numéricas: padronização (média 0, desvio 1) -> coeficientes comparáveis.
    Categórica (região): one-hot encoding.
    O pré-processamento fica DENTRO do pipeline para ser aprendido só com
    os dados de treino (evita vazamento na validação cruzada).
    """
    return ColumnTransformer([
        ("numericas", StandardScaler(), config.NUMERIC_FEATURES),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), config.CATEGORICAL_FEATURES),
    ])


def split_data(df: pd.DataFrame):
    """
    Separação 80/20 estratificada pelo alvo: treino e teste mantêm a mesma
    proporção de detratores. O teste só é usado no fim, uma única vez.
    """
    X = df[config.MODEL_FEATURES]
    y_class = df[config.TARGET_CLASS]
    y_score = df[config.TARGET_SCORE]
    return train_test_split(
        X, y_class, y_score, test_size=config.TEST_SIZE,
        stratify=y_class, random_state=config.RANDOM_STATE,
    )


def classification_candidates() -> dict:
    """Modelos comparados, do mais simples ao mais complexo."""
    return {
        "Baseline (sempre 'detrator')": DummyClassifier(strategy="most_frequent"),
        "Regressão Logística": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, class_weight="balanced", random_state=config.RANDOM_STATE),
        "Gradient Boosting": HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, random_state=config.RANDOM_STATE),
    }


def regression_candidates() -> dict:
    return {
        "Baseline (média)": DummyRegressor(strategy="mean"),
        "Regressão Linear": LinearRegression(),
        "Gradient Boosting": HistGradientBoostingRegressor(
            max_depth=3, learning_rate=0.05, random_state=config.RANDOM_STATE),
    }


def compare_classifiers(X_train, y_train) -> pd.DataFrame:
    """Validação cruzada de 5 dobras somente no conjunto de treino."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
    rows = []
    for name, model in classification_candidates().items():
        pipe = Pipeline([("prep", build_preprocessor()), ("modelo", model)])
        scores = cross_validate(pipe, X_train, y_train, cv=cv,
                                scoring=["roc_auc", "average_precision", "recall", "precision", "f1"])
        rows.append({
            "modelo": name,
            "AUC": scores["test_roc_auc"].mean(),
            "AUC_desvio": scores["test_roc_auc"].std(),
            "PR_AUC": scores["test_average_precision"].mean(),
            "recall": scores["test_recall"].mean(),
            "precisao": scores["test_precision"].mean(),
            "F1": scores["test_f1"].mean(),
        })
    return pd.DataFrame(rows).set_index("modelo").round(3)


def compare_regressors(X_train, y_train) -> pd.DataFrame:
    from sklearn.model_selection import KFold
    cv = KFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
    rows = []
    for name, model in regression_candidates().items():
        pipe = Pipeline([("prep", build_preprocessor()), ("modelo", model)])
        scores = cross_validate(pipe, X_train, y_train, cv=cv,
                                scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"])
        rows.append({
            "modelo": name,
            "MAE": -scores["test_neg_mean_absolute_error"].mean(),
            "RMSE": -scores["test_neg_root_mean_squared_error"].mean(),
            "R2": scores["test_r2"].mean(),
        })
    return pd.DataFrame(rows).set_index("modelo").round(3)


def build_final_classifier() -> Pipeline:
    """
    Modelo escolhido: Regressão Logística.
    Motivo: desempenho estatisticamente equivalente aos modelos de árvore
    na validação cruzada, e é explicável (cada variável tem um peso claro),
    o que facilita a adoção pelas áreas de negócio.
    """
    return Pipeline([("prep", build_preprocessor()),
                     ("modelo", LogisticRegression(max_iter=1000, class_weight="balanced"))])


def build_final_regressor() -> Pipeline:
    return Pipeline([("prep", build_preprocessor()), ("modelo", LinearRegression())])


def risk_band(probabilities) -> pd.Series:
    return pd.cut(pd.Series(probabilities), bins=RISK_BINS, labels=RISK_LABELS, right=False)


def evaluate_classifier(model, X_test, y_test, threshold=0.5) -> dict:
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    bands = pd.DataFrame({"faixa": risk_band(proba).values, "real": y_test.values})
    band_table = bands.groupby("faixa", observed=False)["real"].agg(["size", "mean"])
    return {
        "AUC": round(roc_auc_score(y_test, proba), 3),
        "PR_AUC": round(average_precision_score(y_test, proba), 3),
        "recall": round(recall_score(y_test, pred), 3),
        "precisao": round(precision_score(y_test, pred), 3),
        "F1": round(f1_score(y_test, pred), 3),
        "matriz_confusao": {"VN": int(tn), "FP": int(fp), "FN": int(fn), "VP": int(tp)},
        "faixas_risco": {
            str(k): {"pedidos": int(v["size"]), "pct_detratores_real": round(100 * v["mean"], 1)}
            for k, v in band_table.iterrows()
        },
    }


def evaluate_regressor(model, X_test, y_test) -> dict:
    pred = model.predict(X_test)
    return {
        "MAE": round(mean_absolute_error(y_test, pred), 3),
        "RMSE": round(root_mean_squared_error(y_test, pred), 3),
        "R2": round(r2_score(y_test, pred), 3),
    }


def coefficients(model: Pipeline) -> pd.Series:
    """Pesos do modelo linear por variável (dados padronizados)."""
    names = model.named_steps["prep"].get_feature_names_out()
    names = [n.split("__", 1)[1] for n in names]
    coefs = model.named_steps["modelo"].coef_.ravel()
    return pd.Series(coefs, index=names).sort_values()


def main():
    df = prepare_dataset(load_raw_data())
    X_train, X_test, yc_train, yc_test, ys_train, ys_test = split_data(df)

    print("== Comparação de classificadores (validação cruzada no treino) ==")
    clf_cv = compare_classifiers(X_train, yc_train)
    print(clf_cv)
    print("\n== Comparação de regressores (validação cruzada no treino) ==")
    reg_cv = compare_regressors(X_train, ys_train)
    print(reg_cv)

    classifier = build_final_classifier().fit(X_train, yc_train)
    regressor = build_final_regressor().fit(X_train, ys_train)

    metrics = {
        "comparacao_classificadores_cv": clf_cv.reset_index().to_dict(orient="records"),
        "comparacao_regressores_cv": reg_cv.reset_index().to_dict(orient="records"),
        "classificador_teste": evaluate_classifier(classifier, X_test, yc_test),
        "regressor_teste": evaluate_regressor(regressor, X_test, ys_test),
        "baseline_regressor_teste_MAE": round(mean_absolute_error(ys_test, np.full(len(ys_test), ys_train.mean())), 3),
        "taxa_detratores_teste": round(100 * yc_test.mean(), 1),
    }
    print("\n== Teste (dados nunca vistos) ==")
    print(json.dumps({k: metrics[k] for k in ["classificador_teste", "regressor_teste"]}, indent=2, ensure_ascii=False))

    config.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(classifier, config.CLASSIFIER_PATH)
    joblib.dump(regressor, config.REGRESSOR_PATH)
    config.METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\nModelos salvos em {config.MODELS_DIR}")


if __name__ == "__main__":
    main()
