"""Exporta os seis graficos a partir das tabelas produzidas por analisar.cpp."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent


def ler(caminho):
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas:
        raise ValueError(f"Tabela sem dados: {caminho}")
    return sorted(linhas, key=lambda r: int(r["workers"]))


def grafico(linhas, series, titulo, eixo_y, destino):
    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    for coluna, legenda in series:
        pares = [(int(r["workers"]), float(r[coluna])) for r in linhas if r[coluna] != ""]
        if not pares:
            continue
        x, y = zip(*pares)
        estilo = "--" if coluna.endswith("ideal") else "-"
        ax.plot(x, y, estilo, marker="o", label=legenda)
    if not ax.lines:
        raise ValueError(f"Nenhuma serie disponivel para {destino.name}")
    ax.set(title=titulo, xlabel="Threads (OpenMP) / processos (MPI)", ylabel=eixo_y)
    ax.set_xticks([int(r["workers"]) for r in linhas])
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(destino, dpi=160)
    plt.close(fig)
    print(f"Gravado {destino}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", type=Path, default=RAIZ / "dados")
    parser.add_argument("--saida", type=Path, default=RAIZ / "graficos")
    args = parser.parse_args()
    forte = ler(args.dados / "tabela_forte_n100000000.csv")
    pequena = ler(args.dados / "tabela_forte_n10000000.csv")
    fraca = ler(args.dados / "tabela_fraca.csv")
    args.saida.mkdir(parents=True, exist_ok=True)
    speedup = [("speedup_openmp", "OpenMP"), ("speedup_mpi", "MPI"), ("speedup_ideal", "Ideal")]
    especificacoes = [
        (forte, [("tempo_sequencial", "Sequencial"), ("tempo_openmp", "OpenMP"), ("tempo_mpi", "MPI")],
         "Tempo: n = 100 milhões", "Tempo (s)", "forte_n100M_tempo.png"),
        (forte, speedup, "Speedup: n = 100 milhões", "Speedup contra o sequencial", "forte_n100M_speedup.png"),
        (forte, [("eficiencia_openmp", "OpenMP"), ("eficiencia_mpi", "MPI"), ("eficiencia_ideal", "Ideal")],
         "Eficiência: n = 100 milhões", "Eficiência (fração)", "forte_n100M_eficiencia.jpg"),
        (pequena, speedup, "Speedup: n = 10 milhões", "Speedup contra o sequencial", "forte_n10M_speedup.png"),
        (fraca, [("tempo_openmp", "OpenMP"), ("tempo_mpi", "MPI")],
         "Escalabilidade fraca: 12,5 milhões por worker", "Tempo (s)", "fraca_tempo.png"),
        (fraca, [("eficiencia_fraca_openmp", "OpenMP"), ("eficiencia_fraca_mpi", "MPI"), ("eficiencia_ideal", "Ideal")],
         "Escalabilidade fraca: 12,5 milhões por worker", "Eficiência fraca (fração)", "fraca_eficiencia.png"),
    ]
    for linhas, series, titulo, eixo_y, nome in especificacoes:
        grafico(linhas, series, titulo, eixo_y, args.saida / nome)


if __name__ == "__main__":
    main()
