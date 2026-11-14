#!/usr/bin/env bash
# Uso: scripts/coletar.sh [forte|fraca|todas]
# Variaveis opcionais:
#   VERSOES="sequencial openmp mpi"   (padrao: todas)
#   OUT=dados/medicoes.csv            (arquivo de saida)
#   MPIRUN_EXTRA="--oversubscribe"    (flags extras do mpirun)
set -euo pipefail
cd "$(dirname "$0")/.."

ESCALA="${1:-todas}"
VERSOES="${VERSOES:-sequencial openmp mpi}"
OUT="${OUT:-dados/medicoes.csv}"
BIN_SEQ="baseline/02_montecarlo_pi"
BIN_OMP="openmp/02_montecarlo_pi_omp"
BIN_MPI="mpi/02_montecarlo_pi_mpi"
GABARITO="dados/gabarito.csv"
N_FORTE=(10000000 50000000 100000000)
WORKERS=(1 2 4 6 8 12)
N_POR_WORKER=12500000

selecionada() { [[ " $VERSOES " == *" $1 "* ]]; }

# Executa um comando e devolve a unica linha "n=..." da saida; falha se nao houver exatamente uma.
executar() {
    local saida linhas
    saida="$("$@")" || { echo "ERRO: falha ao executar: $*" >&2; exit 1; }
    linhas="$(printf '%s\n' "$saida" | grep -E '^n=' || true)"
    if [ "$(printf '%s\n' "$linhas" | grep -c .)" -ne 1 ]; then
        echo "ERRO: esperava exatamente 1 linha 'n=...' de: $*" >&2
        echo "$saida" >&2
        exit 1
    fi
    printf '%s\n' "$linhas"
}

parse() {
    if [[ "$1" =~ n=([0-9]+)[[:space:]]+pi=([0-9.]+)[[:space:]]+dentro=([0-9]+)[[:space:]]+tempo=([0-9.]+) ]]; then
        P_N="${BASH_REMATCH[1]}"; P_PI="${BASH_REMATCH[2]}"
        P_DENTRO="${BASH_REMATCH[3]}"; P_TEMPO="${BASH_REMATCH[4]}"
    else
        echo "ERRO: saida nao reconhecida: '$1'" >&2; exit 1
    fi
}

validar() {  # $1=n $2=pi $3=dentro
    local gp gd
    gp="$(awk -F',' -v n="$1" '$1==n {print $2}' "$GABARITO")"
    gd="$(awk -F',' -v n="$1" '$1==n {print $3}' "$GABARITO")"
    [ -n "$gd" ] || { echo "ERRO: n=$1 sem gabarito em $GABARITO" >&2; exit 1; }
    if [ "$2" = "$gp" ] && [ "$3" = "$gd" ]; then echo OK; else echo DIVERGENTE; fi
}

rodar() {  # $1=versao $2=escala $3=n $4=workers
    local versao="$1" escala="$2" n="$3" p="$4" rep linha status
    local -a cmd
    case "$versao" in
        sequencial) cmd=("$BIN_SEQ" "$n") ;;
        openmp)     cmd=(env OMP_NUM_THREADS="$p" "$BIN_OMP" "$n") ;;
        mpi)        cmd=(mpirun ${MPIRUN_EXTRA:-} -np "$p" "$BIN_MPI" "$n") ;;
    esac
    echo "-- $versao | $escala | n=$n | workers=$p"
    executar "${cmd[@]}" > /dev/null          # aquecimento, descartado
    for rep in 1 2 3; do
        linha="$(executar "${cmd[@]}")"
        parse "$linha"
        status="$(validar "$n" "$P_PI" "$P_DENTRO")"
        echo "$versao,$escala,$n,$p,$rep,$P_TEMPO,$P_PI,$P_DENTRO,$status" >> "$OUT"
    done
}

for v in $VERSOES; do
    case "$v" in
        sequencial) bin="$BIN_SEQ" ;;
        openmp) bin="$BIN_OMP" ;;
        mpi) bin="$BIN_MPI" ;;
        *) echo "ERRO: versao desconhecida: $v" >&2; exit 1 ;;
    esac
    [ -x "$bin" ] || { echo "ERRO: executavel nao encontrado: $bin" >&2; exit 1; }
done
[ -f "$GABARITO" ] || { echo "ERRO: rode scripts/gerar_gabarito.sh antes" >&2; exit 1; }

mkdir -p dados
echo "versao,escala,n,workers,repeticao,tempo_s,pi_estimado,dentro,status_validacao" > "$OUT"

if [[ "$ESCALA" == forte || "$ESCALA" == todas ]]; then
    for n in "${N_FORTE[@]}"; do
        selecionada sequencial && rodar sequencial forte "$n" 1
        for p in "${WORKERS[@]}"; do
            selecionada openmp && rodar openmp forte "$n" "$p"
            selecionada mpi && rodar mpi forte "$n" "$p"
        done
    done
fi

if [[ "$ESCALA" == fraca || "$ESCALA" == todas ]]; then
    for p in "${WORKERS[@]}"; do
        n=$((N_POR_WORKER * p))
        selecionada sequencial && rodar sequencial fraca "$n" 1
        selecionada openmp && rodar openmp fraca "$n" "$p"
        selecionada mpi && rodar mpi fraca "$n" "$p"
    done
fi

echo "Medicoes gravadas em $OUT"