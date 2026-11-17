"""Corretude e medicao separada da coleta do Gui; escreve somente em openmp/."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone


PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
WORKERS = (1, 2, 4, 6, 8, 12)
LINHA = re.compile(
    r"n=(-?\d+)  pi=(\S+)  dentro=(\d+)  tempo=(\d+\.\d{6}) s"
)
# Expressao do parser do Gui, usada para as entradas positivas do gabarito.
PARSER_GUI = re.compile(
    r"n=([0-9]+)\s+pi=([0-9.]+)\s+dentro=([0-9]+)\s+tempo=([0-9.]+)"
)


def executar(comando, env=None):
    processo = subprocess.run(
        [str(item) for item in comando], env=env, capture_output=True,
        text=True, check=True, timeout=120,
    )
    if processo.stderr:
        raise RuntimeError(f"stderr inesperado: {processo.stderr}")
    return processo.stdout.strip()


def ambiente(p, extras=None):
    env = dict(os.environ, OMP_NUM_THREADS=str(p), OMP_DYNAMIC="FALSE")
    if extras:
        env.update(extras)
    return env


def resultado(binario, argumentos, p=1, extras=None):
    saida = executar([binario, *argumentos], ambiente(p, extras))
    m = LINHA.fullmatch(saida)
    if not m:
        raise RuntimeError(f"Contrato de saida invalido: {saida!r}")
    n, pi, dentro, tempo = m.groups()
    return (n, pi, dentro), float(tempo), saida


def escritor(caminho, campos):
    arquivo = caminho.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(arquivo, fieldnames=campos)
    writer.writeheader()
    return arquivo, writer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sufixo = ".exe" if os.name == "nt" else ""
    parser.add_argument("--seq", type=Path, default=PASTA / ".build" / ("baseline_original" + sufixo))
    parser.add_argument("--omp", type=Path, default=PASTA / ("02_montecarlo_pi_omp" + sufixo))
    parser.add_argument("--unit", type=Path, default=PASTA / ".build" / ("testar_jump" + sufixo))
    parser.add_argument("--saida", type=Path, default=PASTA / ".build" / "resultados")
    parser.add_argument("--medir", action="store_true")
    args = parser.parse_args()
    saida = args.saida.resolve()
    if not saida.is_relative_to(PASTA) or saida == PASTA:
        parser.error("--saida deve ser um subdiretorio de openmp/")
    try:
        saida.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("--saida ja existe; escolha um novo diretorio para preservar os registros anteriores")
    cpus = getattr(os, "process_cpu_count", os.cpu_count)() or 1
    workers = [p for p in WORKERS if p <= cpus]
    registro = {
        "inicio_utc": datetime.now(timezone.utc).isoformat(),
        "plataforma": platform.platform(), "python": sys.version,
        "cpus_logicas_disponiveis": cpus, "workers_testados": workers,
        "workers_omitidos_por_limite": [p for p in WORKERS if p > cpus],
        "final_no_laboratorio": False,
        "classificacao": "diagnostico; repetir no Linux da disciplina",
        "baseline_sha256": hashlib.sha256((RAIZ / "baseline/02_montecarlo_pi.cpp").read_bytes()).hexdigest(),
        "fontes_sha256": {
            nome: hashlib.sha256((PASTA / nome).read_bytes()).hexdigest()
            for nome in ("02_montecarlo_pi_openmp.cpp", "xorshift_jump.h", "testar_jump.cpp")
        },
        "binarios": {nome: str(getattr(args, nome).resolve()) for nome in ("seq", "omp", "unit")},
        "compilador": executar(["g++", "--version"]),
        "omp_ambiente_original": {k: v for k, v in os.environ.items() if k.startswith("OMP_")},
        "omp_dynamic_medicoes": "FALSE",
    }
    print(executar([args.unit]), flush=True)
    equipes = {}
    for p in workers:
        probe = executar([args.unit, "--equipe"], ambiente(p))
        if probe != f"threads={p}":
            raise RuntimeError(f"Equipe menor que a solicitada: p={p}, {probe}")
        equipes[str(p)] = p
    registro["equipes_reais_probe"] = equipes
    (saida / "ambiente.json").write_text(json.dumps(registro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PASTA / "gabarito_referencia.csv").open(encoding="utf-8") as f:
        gabarito = {int(r["n"]): (r["n"], r["pi_estimado"], r["dentro"]) for r in csv.DictReader(f)}

    arquivo, writer = escritor(saida / "corretude.csv", ["argumentos", "workers", "repeticao", "n", "pi", "dentro", "status"])
    quantidade = 0
    try:
        pequenos = [[], *[[str(n)] for n in (-7, -1, 0, 1, 2, 3, 5, 7, 11, 12, 13, 17, 31, 63, 64, 65, 97, 257, 1001, 100003)],
                    ["abc"], ["17abc"], [" 17"]]
        casos = pequenos + [[str(n)] for n in gabarito]
        for argumentos in casos:
            esperado, _, _ = resultado(args.seq, argumentos)
            if argumentos and argumentos[0].isdigit() and int(argumentos[0]) in gabarito:
                if esperado != gabarito[int(argumentos[0])]:
                    raise RuntimeError(f"Baseline diverge do gabarito: {argumentos}: {esperado}")
            for p in workers:
                for rep in (1, 2):
                    obtido, _, linha = resultado(args.omp, argumentos, p)
                    if obtido != esperado:
                        raise RuntimeError(f"Divergencia: args={argumentos}, p={p}: {obtido} != {esperado}")
                    if int(obtido[0]) in gabarito and not PARSER_GUI.fullmatch(linha[:-2]):
                        raise RuntimeError("Saida incompatível com parser do Gui")
                    writer.writerow(dict(zip(writer.fieldnames, [json.dumps(argumentos), p, rep, *obtido, "OK"])))
                    quantidade += 1
            print(f"OK args={argumentos or '[padrao]'}: {esperado}", flush=True)
        # Forca equipe menor que OMP_NUM_THREADS, verificando uso do tamanho real.
        for extras in ({"OMP_THREAD_LIMIT": "3"}, {"OMP_DYNAMIC": "TRUE"}):
            esperado, _, _ = resultado(args.seq, ["100003"])
            obtido, _, _ = resultado(args.omp, ["100003"], 12, extras)
            if obtido != esperado:
                raise RuntimeError(f"Divergencia com equipe ajustada: {extras}")
            writer.writerow(dict(zip(writer.fieldnames, [json.dumps(extras), 12, 1, *obtido, "OK"])))
            quantidade += 1
    finally:
        arquivo.close()
    print(f"Corretude: {quantidade} comparacoes OpenMP aprovadas.", flush=True)
    if not args.medir:
        return

    campos = ["versao", "escala", "n", "workers", "repeticao", "tempo_s", "pi_estimado", "dentro", "status_validacao"]
    arquivo, writer = escritor(saida / "medicoes.csv", campos)
    arquivo_aq, writer_aq = escritor(saida / "aquecimentos.csv", campos)
    tempos = {}
    configuracoes = [("forte", n, workers) for n in (10000000, 50000000, 100000000)]
    configuracoes += [("fraca", 12500000 * p, [p]) for p in workers]
    try:
        for escala, n, ps in configuracoes:
            versoes = [("sequencial", args.seq, 1)] + [("openmp", args.omp, p) for p in ps]
            for versao, binario, p in versoes:
                ts = []
                for rep in (0, 1, 2, 3):
                    obtido, tempo, _ = resultado(binario, [str(n)], p)
                    if obtido != gabarito[n]:
                        raise RuntimeError(f"Divergencia durante medicao: {escala}, {n}, {p}, {obtido}")
                    linha = dict(zip(campos, [versao, escala, n, p, rep, f"{tempo:.6f}", obtido[1], obtido[2], "OK"]))
                    (writer_aq if rep == 0 else writer).writerow(linha)
                    if rep:
                        ts.append(tempo)
                tempos[(escala, n, versao, p)] = statistics.median(ts)
                print(f"Mediana diagnostica: {escala} {versao} n={n} p={p}: {statistics.median(ts):.6f} s", flush=True)
    finally:
        arquivo.close()
        arquivo_aq.close()
    campos_resumo = ["escala", "n", "workers", "t_seq_s", "t_omp_s", "speedup_seq", "eficiencia_seq", "speedup_omp1", "eficiencia_fraca"]
    arquivo, writer = escritor(saida / "resumo.csv", campos_resumo)
    try:
        for (escala, n, versao, p), tempo in tempos.items():
            if versao != "openmp":
                continue
            seq = tempos[(escala, n, "sequencial", 1)]
            omp1 = tempos.get((escala, n, "openmp", 1))
            fraca = tempos.get(("fraca", 12500000, "openmp", 1)) if escala == "fraca" else None
            writer.writerow(dict(zip(campos_resumo, [escala, n, p, f"{seq:.6f}", f"{tempo:.6f}", f"{seq/tempo:.6f}", f"{seq/tempo/p:.6f}", f"{omp1/tempo:.6f}" if omp1 else "", f"{fraca/tempo:.6f}" if fraca else ""])))
    finally:
        arquivo.close()
    print(f"Registros diagnosticos salvos em {saida}", flush=True)


if __name__ == "__main__":
    main()
