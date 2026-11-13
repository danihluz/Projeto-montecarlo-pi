#!/usr/bin/env python3
"""Validacao MPI e execucao dos scripts intactos do PR #14 numa copia isolada."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

MPI = Path(__file__).resolve().parent
REPO = MPI.parent
TEMP = MPI / ".testes"
RESULTADOS = MPI / "resultados"
PR_SHA = "e0917954201eeb854f094f36b9f94f41a3dd81a1"
PADRAO = re.compile(r"n=([0-9]+)  pi=([0-9]+\.[0-9]{6})  "
                    r"dentro=([0-9]+)  tempo=([0-9]+\.[0-9]{6}) s\n")


def main():
    TEMP.mkdir(exist_ok=True)
    RESULTADOS.mkdir(exist_ok=True)
    log = (RESULTADOS / "validacao.log").open("w", encoding="utf-8", newline="\n")

    def executar(args, cwd=REPO, timeout=180, falha_esperada=False, env=None):
        log.write("$ " + " ".join(map(str, args)) + "\n")
        log.flush()
        proc = subprocess.run(list(map(str, args)), cwd=cwd, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=timeout, env=env)
        log.write(re.sub(r"[ \t]+\n", "\n", proc.stdout))
        if proc.stderr:
            log.write("STDERR:\n" + proc.stderr)
        log.write(f"exit={proc.returncode}\n")
        log.flush()
        if (proc.returncode != 0) != falha_esperada:
            raise RuntimeError(f"retorno inesperado: {args}: {proc.returncode}")
        return proc

    def analisar_saida(proc, n):
        match = PADRAO.fullmatch(proc.stdout)
        if not match or int(match[1]) != n:
            raise RuntimeError(f"saida fora do contrato: {proc.stdout!r}")
        if proc.stderr:
            raise RuntimeError(f"stderr inesperado: {proc.stderr}")
        return match[2], match[3], match[4]

    try:
        comando_mpi = ["mpirun"] + shlex.split(os.environ.get("MPIRUN_EXTRA", ""))
        cpus = len(os.sched_getaffinity(0))
        workers_coletor = [1, 2, 4, 6, 8, 12]
        sobrealocados = [p for p in workers_coletor if p > cpus]
        ressalva = (f"Processos acima das {cpus} CPUs disponiveis: {sobrealocados}; "
                    "esses casos verificam compatibilidade sob sobrealocacao.")
        maquina = [f"Data: {datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}",
                   f"CPUs logicas disponiveis: {cpus}",
                   f"PR #14 inspecionado: {PR_SHA}",
                   ("MPI extraido localmente; nenhum pacote instalado no sistema."
                    if os.environ.get("MPI_DANI_ROOT") else "MPI encontrado no PATH."),
                   ressalva]
        for cmd in (["uname", "-a"], ["cat", "/etc/os-release"], ["lscpu"],
                    ["free", "-h"], ["g++", "--version"], ["mpirun", "--version"]):
            maquina.append("$ " + " ".join(cmd) + "\n" + executar(cmd).stdout)
        for key in ("HYDRA_LAUNCHER", "UCX_TLS", "OMP_NUM_THREADS", "MPIRUN_EXTRA"):
            maquina.append(f"{key}={os.environ.get(key, '(nao definida)')}")
        (RESULTADOS / "maquina.txt").write_text(
            re.sub(r"[ \t]+\n", "\n", "\n".join(maquina)), encoding="utf-8")

        executar(["make", "-C", MPI, "all", "teste_jump_ahead"])
        jump = executar([MPI / "teste_jump_ahead"]).stdout.strip()
        print(jump, flush=True)

        # Compila o arquivo original para outro destino; preserva o binario existente.
        seq = TEMP / "02_montecarlo_pi_seq"
        executar(["g++", "-O2", "-o", seq, REPO / "baseline/02_montecarlo_pi.cpp"])
        bin_mpi = MPI / "02_montecarlo_pi_mpi"

        copia = TEMP / "pr14"
        arquivos = ["scripts/coletar.sh", "scripts/analisar.cpp",
                    "dados/gabarito.csv", "secoes/protocolo_medicao.md"]
        origens = {}
        for arquivo in arquivos:
            url = ("https://raw.githubusercontent.com/danihluz/Projeto-montecarlo-pi/"
                   + PR_SHA + "/" + arquivo)
            with urllib.request.urlopen(url, timeout=60) as response:
                conteudo = response.read()
            destino = copia / arquivo
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(conteudo)
            origens[arquivo] = {"url": url, "sha256": hashlib.sha256(conteudo).hexdigest()}
        (RESULTADOS / "origens_pr14.json").write_text(
            json.dumps(origens, indent=2) + "\n", encoding="utf-8")

        gabarito = {}
        texto = (copia / "dados/gabarito.csv").read_text(encoding="utf-8")
        for row in csv.DictReader(io.StringIO(texto)):
            gabarito[int(row["n"])] = row["pi_estimado"], row["dentro"]

        workers = [p for p in (1, 2, 3, 4, 6, 8) if p <= cpus]
        pequenos = [1, 2, 3, 5, 7, 10, 17, 31, 1001, 10003, 10000003]
        comparacoes = 0
        with (RESULTADOS / "comparacoes.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["n", "workers", "pi_baseline", "dentro_baseline",
                             "pi_mpi", "dentro_mpi", "tempo_mpi_s", "status"])
            for n in pequenos + sorted(gabarito):
                pi_seq, dentro_seq, _ = analisar_saida(executar([seq, n]), n)
                if n in gabarito and (pi_seq, dentro_seq) != gabarito[n]:
                    raise RuntimeError(f"baseline difere do gabarito para n={n}")
                for p in workers:
                    pi_mpi, dentro_mpi, tempo = analisar_saida(
                        executar(comando_mpi + ["-np", p, bin_mpi, n]), n)
                    if (pi_seq, dentro_seq) != (pi_mpi, dentro_mpi):
                        raise RuntimeError(f"divergencia para n={n}, p={p}")
                    writer.writerow([n, p, pi_seq, dentro_seq, pi_mpi,
                                     dentro_mpi, tempo, "OK"])
                    comparacoes += 1
                f.flush()
                print(f"OK: n={n}; processos={workers}", flush=True)

        # Confere tambem o argumento omitido (50 milhoes).
        esperado = analisar_saida(executar([seq]), 50000000)[:2]
        padrao = analisar_saida(executar(comando_mpi + ["-np", 4, bin_mpi]), 50000000)
        if padrao[:2] != esperado:
            raise RuntimeError("divergencia com argumento omitido")

        # A identificacao de rank do Hydra comprova a origem da unica linha.
        versao_mpi = executar(["mpirun", "--version"]).stdout
        rank = "uma linha exata em todas as comparacoes; impressao condicionada a rank 0 no codigo"
        if "HYDRA" in versao_mpi:
            proc = executar(comando_mpi + ["-l", "-np", 4, bin_mpi, 17])
            if not proc.stdout.startswith("[0] ") or not PADRAO.fullmatch(proc.stdout[4:]):
                raise RuntimeError("saida etiquetada nao veio apenas do rank 0")
            rank = proc.stdout.strip()

        for n in (0, -1):
            proc = executar(comando_mpi + ["-np", 4, bin_mpi, n], falha_esperada=True)
            # OpenMPI tambem relata o retorno nao zero dos processos no stderr.
            if proc.stdout or proc.stderr.splitlines().count("ERRO: n deve ser positivo.") != 1:
                raise RuntimeError("entrada invalida nao foi rejeitada como esperado")

        # Mantem os scripts do Gui byte a byte, inclusive WORKERS=(1 2 4 6 8 12).
        # Hydra permite 12 processos locais, inclusive em CPUs sobrealocadas.
        for arquivo, origem in origens.items():
            if hashlib.sha256((copia / arquivo).read_bytes()).hexdigest() != origem["sha256"]:
                raise RuntimeError(f"copia do PR foi alterada: {arquivo}")
        (copia / "baseline").mkdir(exist_ok=True)
        (copia / "mpi").mkdir(exist_ok=True)
        shutil.copy2(seq, copia / "baseline/02_montecarlo_pi")
        shutil.copy2(bin_mpi, copia / "mpi/02_montecarlo_pi_mpi")
        # O coletor permite selecionar as versoes por ambiente.
        coleta_env = dict(os.environ, VERSOES="sequencial mpi",
                          OUT="dados/medicoes.csv")
        print("Executando coletor intacto do Gui (forte e fraca)... " + ressalva, flush=True)
        executar(["bash", "scripts/coletar.sh", "todas"], cwd=copia,
                 timeout=600, env=coleta_env)

        with (copia / "dados/medicoes.csv").open() as f:
            medicoes = list(csv.DictReader(f))
        if len(medicoes) != 99 or any(r["status_validacao"] != "OK" for r in medicoes):
            raise RuntimeError("coleta incompleta ou divergente (esperadas 99 medicoes)")
        executar(["g++", "-O2", "-std=c++17", "-o", "scripts/analisar",
                  "scripts/analisar.cpp"], cwd=copia)
        executar(["scripts/analisar"], cwd=copia)
        for nome in ("medicoes.csv", "resumo.csv", "tabela_fraca.csv",
                     "tabela_forte_n10000000.csv", "tabela_forte_n50000000.csv",
                     "tabela_forte_n100000000.csv"):
            shutil.copy2(copia / "dados" / nome, RESULTADOS / nome)
        resumo = {"status": "OK", "jump_ahead": jump,
                  "comparacoes_baseline_mpi": comparacoes,
                  "medicoes_coletor_gui": len(medicoes), "rank_0": rank,
                  "argumento_omitido": "OK", "entradas_invalidas": "0 e -1 rejeitadas",
                  "cpus_disponiveis": cpus, "workers_coletor": workers_coletor,
                  "sobrealocacao": ressalva,
                  "pr14_commit": PR_SHA}
        (RESULTADOS / "validacao.json").write_text(
            json.dumps(resumo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"OK: {comparacoes} comparacoes exatas; {len(medicoes)} medicoes do coletor OK.",
              flush=True)
    except Exception as exc:
        log.write(f"FALHA: {exc}\n")
        (RESULTADOS / "validacao.json").write_text(
            json.dumps({"status": "FALHA", "erro": str(exc)}, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        log.close()


if __name__ == "__main__":
    main()
