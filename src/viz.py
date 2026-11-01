"""
Funções de visualização padronizadas.

Todos os gráficos seguem o mesmo estilo: fundo limpo, grade discreta,
uma única cor de destaque e título que já conta a conclusão
(ex.: "Atraso de 2 dias já gera 88% de detratores").
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

from src import config


def set_style() -> None:
    """Aplica o estilo visual do projeto em todos os gráficos."""
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb",
        "axes.edgecolor": "#c3c2b7",
        "axes.labelcolor": config.COLOR_TEXT_SECONDARY,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 14,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": config.COLOR_GRID,
        "grid.linewidth": 0.8,
        "xtick.color": config.COLOR_TEXT_SECONDARY,
        "ytick.color": config.COLOR_TEXT_SECONDARY,
        "font.size": 10.5,
        "axes.axisbelow": True,
        "font.family": "DejaVu Sans",
        "legend.frameon": False,
    })


SOURCE_NOTE = "Fonte: base desafio_nps_fase_1.csv (2.500 pedidos). Elaboração própria."


def save(fig, name: str, source: bool = True, source_y: float = -0.03) -> None:
    """
    Salva a figura em reports/figures com nome padronizado.
    Por padrão, inclui a nota de fonte dos dados no rodapé, como recomenda a
    boa prática de visualização (título, unidade, legenda e fonte).
    """
    if source:
        fig.text(0.01, source_y, SOURCE_NOTE, fontsize=8, color=config.COLOR_TEXT_SECONDARY, ha="left", va="top")
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURES_DIR / f"{name}.png", bbox_inches="tight")


def summarize_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Agrupa a base por uma coluna e calcula os indicadores de negócio:
    quantidade de pedidos, nota média, % detratores, % promotores e NPS.
    """
    grouped = df.groupby(column, observed=True).agg(
        pedidos=(config.TARGET_SCORE, "size"),
        nota_media=(config.TARGET_SCORE, "mean"),
        pct_detratores=(config.TARGET_CLASS, "mean"),
        pct_promotores=(config.NPS_CATEGORY, lambda s: (s == "Promotor").mean()),
    )
    grouped["nps"] = 100 * (grouped["pct_promotores"] - grouped["pct_detratores"])
    grouped["pct_detratores"] *= 100
    grouped["pct_promotores"] *= 100
    return grouped.round(1)


def bar_detractor_rate(summary: pd.DataFrame, title: str, xlabel: str,
                       highlight_from=None, ax=None, ylim=105):
    """
    Barras com o % de detratores por faixa. As faixas a partir de
    `highlight_from` ficam em vermelho (zona crítica); as demais em cinza.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4.2))
    labels = [str(i) for i in summary.index]
    colors = []
    crossed = highlight_from is None
    for label in labels:
        if highlight_from is not None and label == str(highlight_from):
            crossed = True
        colors.append(config.COLOR_DETRACTOR if crossed and highlight_from is not None else config.COLOR_CONTEXT)
    if highlight_from is None:
        colors = [config.COLOR_MAIN] * len(labels)
    bars = ax.bar(labels, summary["pct_detratores"], color=colors, width=0.62, edgecolor="#fcfcfb", linewidth=2)
    for bar, value, n in zip(bars, summary["pct_detratores"], summary["pedidos"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value:.0f}%",
                ha="center", va="bottom", fontsize=10, color=config.COLOR_TEXT, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, 3, f"n={n}",
                ha="center", va="bottom", fontsize=8, color="#fcfcfb")
    ax.set_ylim(0, ylim)
    ax.set_ylabel("% de clientes detratores")
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    return ax
