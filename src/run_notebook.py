"""
Executor simples de notebooks (alternativa leve ao `jupyter nbconvert --execute`).

Lê um .ipynb, executa as células de código em sequência num mesmo
namespace, captura textos, tabelas e gráficos, e grava as saídas de volta
no notebook. Útil para regenerar todos os resultados sem abrir o Jupyter.

Uso:
    python -m src.run_notebook notebooks/02_analise_exploratoria.ipynb
"""
import base64
import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _display_factory(outputs):
    def display(obj):
        if hasattr(obj, "_repr_html_") and obj._repr_html_() is not None:
            outputs.append({"output_type": "display_data", "metadata": {},
                            "data": {"text/html": obj._repr_html_(), "text/plain": repr(obj)}})
        else:
            outputs.append({"output_type": "display_data", "metadata": {}, "data": {"text/plain": repr(obj)}})
    return display


def _flush_figures(outputs):
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        outputs.append({"output_type": "display_data", "metadata": {},
                        "data": {"image/png": base64.b64encode(buffer.getvalue()).decode(), "text/plain": "<Figure>"}})
    plt.close("all")


def run(path: str) -> None:
    path = Path(path).resolve()
    notebook = json.loads(path.read_text(encoding="utf-8"))
    os.chdir(path.parent)
    sys.path.insert(0, str(path.parent.parent))
    namespace = {"__name__": "__main__"}
    counter = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        counter += 1
        outputs = []
        namespace["display"] = _display_factory(outputs)
        source = "".join(cell["source"])
        lines = source.rstrip().split("\n")
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                # Se a última linha for uma expressão, mostra seu valor (como o Jupyter faz)
                body, last = "\n".join(lines[:-1]), lines[-1]
                try:
                    compile(last, "<cell>", "eval")
                    is_expr = not last.startswith((" ", "\t")) and not last.rstrip().endswith(";")
                except SyntaxError:
                    is_expr = False
                if is_expr:
                    exec(compile(body, "<cell>", "exec"), namespace)
                    value = eval(compile(last, "<cell>", "eval"), namespace)
                else:
                    exec(compile(source, "<cell>", "exec"), namespace)
                    value = None
        except Exception:
            print(stdout.getvalue())
            traceback.print_exc()
            raise SystemExit(f"Erro na célula {counter} de {path.name}")
        text = stdout.getvalue()
        if text:
            outputs.insert(0, {"output_type": "stream", "name": "stdout", "text": text})
        _flush_figures(outputs)
        if value is not None:
            data = {"text/plain": repr(value)}
            if hasattr(value, "_repr_html_") and value._repr_html_():
                data["text/html"] = value._repr_html_()
            outputs.append({"output_type": "execute_result", "execution_count": counter, "metadata": {}, "data": data})
        cell["outputs"] = outputs
        cell["execution_count"] = counter
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {path.name} ({counter} células executadas)")


if __name__ == "__main__":
    # Resolve todos os caminhos antes, pois run() muda o diretório atual
    for nb in [Path(p).resolve() for p in sys.argv[1:]]:
        run(nb)
