#!/usr/bin/env bash
# Gera dados/gabarito.csv rodando o baseline (2x por n, para checar repetibilidade).
set -euo pipefail
cd "$(dirname "$0")/.."

BIN="baseline/02_montecarlo_pi"
OUT="dados/gabarito.csv"
NS=(10000000 12500000 25000000 50000000 75000000 100000000 150000000)

make baseline
mkdir -p dados
echo "n,pi_estimado,dentro" > "$OUT"

for n in "${NS[@]}"; do
    a="$("$BIN" "$n")"
    b="$("$BIN" "$n")"
    [[ "$a" =~ pi=([0-9.]+)[[:space:]]+dentro=([0-9]+) ]] || { echo "ERRO: saida inesperada: $a" >&2; exit 1; }
    pi_a="${BASH_REMATCH[1]}"; d_a="${BASH_REMATCH[2]}"
    [[ "$b" =~ pi=([0-9.]+)[[:space:]]+dentro=([0-9]+) ]] || { echo "ERRO: saida inesperada: $b" >&2; exit 1; }
    if [ "$pi_a" != "${BASH_REMATCH[1]}" ] || [ "$d_a" != "${BASH_REMATCH[2]}" ]; then
        echo "ERRO: baseline nao repetivel para n=$n" >&2; exit 1
    fi
    echo "$n,$pi_a,$d_a" >> "$OUT"
    echo "n=$n pi=$pi_a dentro=$d_a"
done
echo "Gabarito gravado em $OUT"