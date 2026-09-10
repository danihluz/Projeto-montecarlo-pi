#!/usr/bin/env bash
# scripts/medir_perfilamento.sh
#
# Compila baseline/02_montecarlo_pi_perfilamento.cpp e executa (aquecimento
# + 3 execucoes validas) para os mesmos tamanhos de entrada do baseline,
# extraindo a linha "PERFIL,..." (stderr) de cada execucao e calculando
# a mediana de tempo_total_s / tempo_laco_s / tempo_outros_s por n.
# Grava tudo em dados/perfilamento.csv.

set -euo pipefail

SRC="baseline/02_montecarlo_pi_perfilamento.cpp"
BIN="baseline/02_montecarlo_pi_perfilamento"
OUT="dados/perfilamento.csv"
ENTRADAS=(10000000 50000000 100000000)

mkdir -p dados

echo "== Compilando $SRC com g++ -O2 =="
g++ -O2 -o "$BIN" "$SRC"

echo "n,trecho,tempo_s,percentual" > "$OUT"

for n in "${ENTRADAS[@]}"; do
    echo ""
    echo "=== n = $n ==="

    echo "-- Execucao de aquecimento (descartada) --"
    "$BIN" "$n" > /dev/null 2>/dev/null

    totais=() lacos=() outros=()
    for exec_id in 1 2 3; do
        echo "-- Execucao valida $exec_id --"
        linha=$("$BIN" "$n" 2>&1 >/dev/null | grep '^PERFIL')
        echo "   $linha"

        t_total=$(echo "$linha"  | grep -oP 'tempo_total_s=\K[0-9.]+')
        t_laco=$(echo "$linha"   | grep -oP 'tempo_laco_s=\K[0-9.]+')
        t_outros=$(echo "$linha" | grep -oP 'tempo_outros_s=\K[0-9.]+')

        totais+=("$t_total"); lacos+=("$t_laco"); outros+=("$t_outros")
    done

    mediana_total=$(printf '%s\n' "${totais[@]}" | sort -n | sed -n '2p')
    mediana_laco=$(printf '%s\n'  "${lacos[@]}"  | sort -n | sed -n '2p')
    mediana_outros=$(printf '%s\n' "${outros[@]}" | sort -n | sed -n '2p')

    pct_laco=$(echo "scale=4; $mediana_laco / $mediana_total * 100" | bc)
    pct_outros=$(echo "scale=4; $mediana_outros / $mediana_total * 100" | bc)

    echo "$n,laco_principal,$mediana_laco,$pct_laco" >> "$OUT"
    echo "$n,outros_trechos,$mediana_outros,$pct_outros" >> "$OUT"
    echo "$n,total,$mediana_total,100" >> "$OUT"

    echo "-> n=$n  total=${mediana_total}s  laco=${mediana_laco}s (${pct_laco}%)  outros=${mediana_outros}s (${pct_outros}%)"
done

echo ""
echo "Resultados gravados em $OUT"
echo "Lembre-se de registrar em secoes/perfilamento_amdahl.md que essa instrumentacao"
echo "(duas marcas de tempo extras em main) pode introduzir um pequeno overhead de medicao."