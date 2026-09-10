# Metodologia e Resultados do Baseline

## Metodologia

- **Compilação**: `g++ -O2 -o baseline/02_montecarlo_pi baseline/02_montecarlo_pi.cpp`
- **Ambiente**: contêiner Linux (Dev Container / Docker) fornecido pela
  disciplina, executado sobre WSL2.
- **Tamanhos de entrada (`n`)**: 10.000.000, 50.000.000 e 100.000.000.
- **Protocolo por tamanho**: 1 execução de aquecimento (descartada,
  usada apenas para "aquecer" cache e evitar efeitos de primeira
  execução) seguida de 3 execuções válidas.
- **Tempo registrado**: o valor `tempo` já impresso pelo próprio
  programa, medido internamente com `clock_gettime(CLOCK_MONOTONIC)`
  ao redor do laço principal — não foi usada nenhuma medição externa
  adicional.
- **Métrica final de tempo por `n`**: mediana das 3 execuções válidas.
- **Repetibilidade**: verificada automaticamente pelo script
  (`scripts/medir_baseline.sh`) — `pi_estimado` e `dentro` são
  idênticos entre as 3 execuções válidas de cada `n`, o que é
  esperado, já que o gerador `xorshift64` usa semente fixa
  (`88172645463325252ULL`).
- **Automação**: todas as medições foram feitas pelo script
  `scripts/medir_baseline.sh`, que compila o baseline, executa o
  protocolo acima para os três tamanhos e grava os resultados em
  `dados/baseline.csv`.

## Resultados

| n | execução | pi estimado | dentro | tempo (s) |
|---|---|---|---|---|
| 10.000.000 | 1 | 3.141412 | 7.853.529 | 0.039873 |
| 10.000.000 | 2 | 3.141412 | 7.853.529 | 0.040068 |
| 10.000.000 | 3 | 3.141412 | 7.853.529 | 0.038135 |
| 10.000.000 | **mediana** | — | — | **0.039873** |
| 50.000.000 | 1 | 3.141429 | 39.267.859 | 0.190293 |
| 50.000.000 | 2 | 3.141429 | 39.267.859 | 0.195265 |
| 50.000.000 | 3 | 3.141429 | 39.267.859 | 0.192925 |
| 50.000.000 | **mediana** | — | — | **0.192925** |
| 100.000.000 | 1 | 3.141499 | 78.537.472 | 0.382950 |
| 100.000.000 | 2 | 3.141499 | 78.537.472 | 0.386707 |
| 100.000.000 | 3 | 3.141499 | 78.537.472 | 0.379081 |
| 100.000.000 | **mediana** | — | — | **0.382950** |

Os valores estimados de π ficam próximos de 3,1416 nos três tamanhos,
com o erro absoluto diminuindo levemente à medida que `n` cresce — 
comportamento consistente com a convergência estocástica esperada do
método (ver `secoes/algoritmo_sequencial.md`). O tempo de execução
cresce de forma aproximadamente linear com `n` (de ~0,04s para 10M a
~0,38s para 100M, ou seja, ~10x o tempo para ~10x o `n`), o que é
compatível com a complexidade de tempo O(n) identificada na análise
do algoritmo.

## Caracterização da máquina

```
--- nproc ---
12

--- lscpu ---
Architecture:                x86_64
CPU op-mode(s):              32-bit, 64-bit
Byte Order:                  Little Endian
CPU(s):                      12
On-line CPU(s) list:         0-11
Vendor ID:                   AuthenticAMD
Model name:                  AMD Ryzen 5 3600 6-Core Processor
Thread(s) per core:          2
Core(s) per socket:          6
Socket(s):                   1
Virtualization:              AMD-V
Hypervisor vendor:           Microsoft
Virtualization type:         full
L1d cache:                   192 KiB (6 instances)
L1i cache:                   192 KiB (6 instances)
L2 cache:                    3 MiB (6 instances)
L3 cache:                    16 MiB (1 instance)
NUMA node(s):                1

--- free -h ---
               total        used        free      shared  buff/cache   available
Mem:           7.7Gi       1.9Gi       412Mi        26Mi       5.6Gi       5.8Gi
Swap:          2.0Gi          0B       2.0Gi

--- g++ --version ---
g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
```

O ambiente é um contêiner Linux (Ubuntu 24.04) executado sobre WSL2,
com 12 CPUs lógicas disponíveis (6 núcleos físicos AMD Ryzen 5 3600
com SMT/hyperthreading habilitado) e 7,7 GiB de memória RAM. Essa
caracterização é relevante para a etapa de perfilamento e para a
análise da Lei de Amdahl (`secoes/perfilamento_amdahl.md`), já que
`nproc` = 12 define o limite de unidades de execução fisicamente
disponíveis para uma futura paralelização.