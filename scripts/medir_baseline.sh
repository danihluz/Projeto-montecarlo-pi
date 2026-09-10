#!/usr/bin/env bash
# scripts/medir_baseline.sh
#
# Compila baseline/02_montecarlo_pi.cpp com g++ -O2, executa uma
# rodada de aquecimento (descartada) e três execucoes validas para
# cada tamanho de entrada, e grava tudo em dados/baseline.csv.
#
# O proprio baseline imprime, para cada execucao, uma linha no formato:
#   n=50000000  pi=3.141600  dentro=39270021  tempo=0.512345 s
# onde "tempo" ja e o tempo do laco principal, medido internamente
# com clock_gettime(CLOCK_MONOTONIC). Usamos exatamente esse valor
# (nao um tempo medido por fora) porque e o dado real produzido pelo
# programa.

set -euo pipefail

SRC="baseline/02_montecarlo_pi.cpp"
BIN="baseline/02_montecarlo_pi"
OUT="dados/baseline.csv"
ENTRADAS=(10000000 50000000 100000000)

mkdir -p dados

echo "== Compilando $SRC com g++ -O2 =="
g++ -O2 -o "$BIN" "$SRC"

echo "n,execucao,pi_estimado,dentro,tempo_s" > "$OUT"

for n in "${ENTRADAS[@]}"; do
    echo ""
    echo "=== n = $n ==="

    echo "-- Execucao de aquecimento (descartada) --"
    "$BIN" "$n" > /dev/null

    tempos=()
    for exec_id in 1 2 3; do
        echo "-- Execucao valida $exec_id --"
        saida=$("$BIN" "$n")
        echo "   saida: $saida"

        pi_est=$(echo "$saida"  | grep -oP 'pi=\K[0-9.]+')
        dentro=$(echo "$saida"  | grep -oP 'dentro=\K[0-9]+')
        tempo=$(echo "$saida"   | grep -oP 'tempo=\K[0-9.]+')

        echo "$n,$exec_id,$pi_est,$dentro,$tempo" >> "$OUT"
        tempos+=("$tempo")
        echo "   tempo (laco, medido pelo programa) = ${tempo}s"
    done

    # Mediana dos 3 tempos validos (ordena e pega o do meio)
    mediana=$(printf '%s\n' "${tempos[@]}" | sort -n | sed -n '2p')
    echo "$n,mediana,,,${mediana}" >> "$OUT"
    echo "-> mediana (n=$n) = ${mediana}s"

    # Repetibilidade: confere se pi/dentro se repetem nas 3 execucoes validas
    valores_distintos=$(awk -F',' -v n="$n" '$1==n && $2!="mediana" {print $3","$4}' "$OUT" | sort -u | wc -l)
    if [ "$valores_distintos" -eq 1 ]; then
        echo "-> repetibilidade OK: pi e dentro identicos nas 3 execucoes para n=$n"
    else
        echo "-> ATENCAO: pi/dentro variaram entre execucoes para n=$n (investigar)"
    fi
done

echo ""
echo "== Caracterizacao da maquina =="
{
  echo "--- nproc ---"
  nproc
  echo "--- lscpu ---"
  lscpu
  echo "--- free -h ---"
  free -h
  echo "--- g++ --version ---"
  g++ --version
} | tee dados/maquina.txt

echo ""
echo "Resultados gravados em $OUT"
echo "Caracterizacao da maquina gravada em dados/maquina.txt"