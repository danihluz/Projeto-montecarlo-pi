# Análise experimental

Fonte dos números: `dados/resumo.csv`, `dados/tabela_forte_n*.csv`, `dados/tabela_fraca.csv`, `dados/amdahl.csv`. Todos os tempos são medianas de 3 execuções; todas as linhas com `status_validacao = OK` (0 `DIVERGENTE`).

## 1. Ambiente e o que o tempo mede
- Máquina local: AMD Ryzen 5 3600 (6 núcleos físicos, 12 lógicos), WSL2, g++ 13.3.0, Open MPI 4.1.6 (`dados/maquina_medicoes.txt`).
- Laboratório: [PREENCHER: CPU, nproc, flag do mpirun usada] (`dados/maquina_lab.txt`).
- Tempo OpenMP: jump-ahead + região paralela (inclui criação das threads) + redução + cálculo de π.
- Tempo MPI: após `MPI_Barrier` até depois do `MPI_Reduce`, máximo entre ranks; fora `MPI_Init`/`MPI_Finalize`.

## 2. Escalabilidade forte (n = 100M)
Gráficos: `graficos/forte_n100M_tempo.png`, `forte_n100M_speedup.png`, `forte_n100M_eficiencia.png`, `forte_n10M_speedup.png`.

| p | T seq (s) | T OpenMP | T MPI | S OpenMP | S MPI | E OpenMP | E MPI |
|---|---|---|---|---|---|---|---|
| 1 | 0,382 | 0,374 | 0,754 | 1,02 | 0,51 | 1,02 | 0,51 |
| 2 | 0,382 | 0,192 | 0,383 | 1,99 | 1,00 | 1,00 | 0,50 |
| 4 | 0,382 | 0,119 | 0,190 | 3,22 | 2,01 | 0,80 | 0,50 |
| 6 | 0,382 | 0,074 | 0,128 | 5,14 | 2,98 | 0,86 | 0,50 |
| 8 | 0,382 | 0,060 | 0,097 | 6,40 | 3,93 | 0,80 | 0,49 |
| 12 | 0,382 | 0,067 | 0,101 | 5,73 | 3,78 | 0,48 | 0,31 |

Melhor speedup medido: OpenMP 6,40 com 8 threads; MPI 3,93 com 8 processos. Com 12 workers o tempo piora nas duas versões em relação a 8.

## 3. Escalabilidade fraca (12,5M pontos por worker)
Gráficos: `graficos/fraca_tempo.png`, `graficos/fraca_eficiencia.png`.

| p | n | T OpenMP | T MPI | E fraca OpenMP | E fraca MPI |
|---|---|---|---|---|---|
| 1 | 12,5M | 0,047 | 0,094 | 1,00 | 1,00 |
| 4 | 50M | 0,052 | 0,098 | 0,90 | 0,96 |
| 8 | 100M | 0,063 | 0,098 | 0,75 | 0,96 |
| 12 | 150M | 0,092 | 0,117 | 0,51 | 0,80 |

O tempo do MPI fica quase constante até p = 8; o do OpenMP cresce já a partir de p = 4.

## 4. Medido × Amdahl (n = 100M, S = speedup)
Amdahl prevê S ≈ p (f ≈ 0,99998). Previsto − medido:

| p | OpenMP | MPI |
|---|---|---|
| 2 | 0,01 | 1,00 |
| 4 | 0,78 | 1,99 |
| 8 | 1,60 | 4,07 |
| 12 | 6,27 | 8,22 |

O modelo não inclui jump-ahead, criação de threads, comunicação nem SMT.

## 5. Causas
- **Overhead fixo (OpenMP): há evidência.** A eficiência com p = 8 sobe com n: 0,65 (10M), 0,78 (50M), 0,80 (100M). Com p = 12: 0,19, 0,39, 0,48. Com n = 10M e p = 12 o tempo (0,017 s) é maior que com p = 8 (0,0073 s).
- **Núcleos físicos / SMT: consistente com os dados.** Passando de 8 para 12 workers o tempo OpenMP sobe (0,060 → 0,067 s em 100M; 0,031 → 0,041 s em 50M) e a eficiência cai de 0,80 para 0,48. A máquina tem 6 núcleos físicos. É a explicação mais compatível, mas não foi isolada por outro experimento.
- **MPI ≈ 2× mais lento que o baseline já com p = 1: não é overhead de comunicação.** Em p = 1 o MPI leva 0,075 / 0,377 / 0,754 s para n = 10M / 50M / 100M contra 0,038 / 0,190 / 0,374 s do baseline: razão ≈ 2 em todos os n. A eficiência MPI fica em ≈ 0,5 de p = 1 até p = 8, e não depende de n. Com p = 1 não há comunicação, e um custo fixo não manteria a razão constante ao multiplicar n por 10. Logo, o custo está por ponto simulado no programa MPI. **Causa não identificada**; [PREENCHER após perguntar à Dani / testar].
- **Banda de memória, false sharing, desbalanceamento: sem evidência.** O laço quase não acessa memória, a carga por iteração é uniforme, o OpenMP usa `reduction(+:dentro)` com blocos contíguos e o MPI usa blocos contíguos com `MPI_Reduce`. Nada nos dados indica esses efeitos.
- **Queda do OpenMP entre p = 2 e p = 4 (n = 100M): não explicada.** Eficiência 1,00 → 0,80, mas em n = 50M ela é 0,94 e em p = 6 volta a 0,86. A variação entre n sugere ruído do ambiente (WSL2) com apenas 3 repetições.

## 6. Laboratório
[PREENCHER depois de rodar: tabelas de `dados/lab/`, gráficos `graficos/lab_*.png`, e comparar com a máquina local (eficiência a p = 6 e p = 12, e se o MPI continua ≈ 0,5).]

## 7. Limitações
3 repetições com mediana, sem intervalo de confiança; uma máquina de cada tipo; WSL2 pode introduzir variação; escalabilidade fraca com 12,5M pontos por worker.

## 8. Conclusão
Na máquina local, o OpenMP alcançou speedup 6,40 com 8 threads (n = 100M) e perdeu eficiência com 12 workers, o que é compatível com SMT e com overhead fixo para n pequeno. O MPI escala de forma linear até p = 8, mas com um fator constante de ≈ 2 de custo por ponto em relação ao baseline, que não é explicado por comunicação e ainda precisa de causa. [PREENCHER após o laboratório.]