# Análise experimental

As tabelas das seções 2 a 5 descrevem a coleta original do Gui: `dados/resumo.csv`, `dados/tabela_forte_n*.csv`, `dados/tabela_fraca.csv` e `dados/amdahl.csv`. Todos os tempos são medianas de três execuções após aquecimento; as 171 medições têm `status_validacao=OK`. Esses arquivos e seus gráficos originais foram preservados.

As medições MPI em `mpi/resultados/` pertencem à máquina da Dani. A nova coleta em `dados/integracao_local/` é outro experimento local, descrito ao final. Cada speedup utiliza o sequencial da própria coleta; tempos de máquinas diferentes não são combinados.

As métricas são `S_seq(p)=T_seq(n)/T_p(n)` e `S_1(p)=T_1(n)/T_p(n)`, com `T_1` da própria versão paralela. A eficiência correspondente é `E=S/p`. Na escala fraca, `E_fraca=T_versão(12,5M,1)/T_versão(12,5M*p,p)`. As tabelas fortes abaixo usam `S_seq` e `E_seq`. Por exemplo, em 100M com oito processos, o MPI do Gui tem `S_seq≈3,93`, mas `S_1≈7,77`; são referências distintas.

## 1. Ambiente e o que o tempo mede
- Máquina local: AMD Ryzen 5 3600 (6 núcleos físicos, 12 lógicos), WSL2, g++ 13.3.0, Open MPI 4.1.6 (`dados/maquina_medicoes.txt`).
- Laboratório: ainda não há medições ou caracterização disponíveis. Nenhum resultado local foi identificado como resultado do laboratório.
- Tempo OpenMP: jump-ahead + região paralela (inclui criação das threads) + redução + cálculo de π.
- Tempo MPI: após `MPI_Barrier` até depois do `MPI_Reduce`, máximo entre ranks; fora `MPI_Init`/`MPI_Finalize`.

## 2. Escalabilidade forte (n = 100M)
Gráficos: `graficos/forte_n100M_tempo.png`, `forte_n100M_speedup.png`, `forte_n100M_eficiencia.jpg`, `forte_n10M_speedup.png`.

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
- **Custos fixos OpenMP: comportamento compatível.** A eficiência com p = 8 sobe com n: 0,65 (10M), 0,78 (50M), 0,80 (100M). Com p = 12: 0,19, 0,39, 0,48. Com n = 10M e p = 12 o tempo (0,017 s) é maior que com p = 8 (0,0073 s). A preparação dos saltos, criação de threads e redução podem pesar mais em entradas pequenas; esses custos não foram isolados individualmente.
- **Núcleos físicos / SMT: hipótese compatível com os dados.** Passando de 8 para 12 workers o tempo OpenMP sobe (0,060 → 0,067 s em 100M; 0,031 → 0,041 s em 50M) e a eficiência cai de 0,80 para 0,48. A máquina tem 6 núcleos físicos. Esse efeito não foi isolado por outro experimento.
- **MPI com um processo: razão próxima de 2 no ambiente do Gui.** Para 10M / 50M / 100M, `T_MPI(1)` foi 0,075231 / 0,376802 / 0,754306 s e `T_seq` foi 0,038170 / 0,190204 / 0,381986 s: razões próximas de 1,97 / 1,98 / 1,97. A razão quase constante sugere um efeito proporcional ao trabalho. A origem não foi isolada: afinidade/binding, frequência, compilador, runtime MPI e condições de execução podem afetar o custo observado. Com um processo não há tráfego entre ranks distintos, mas permanecem chamadas ao runtime. A coleta não permite atribuir o fator ao código, à comunicação ou a um gargalo específico. A investigação local adicional é apresentada ao final; a causa histórica permanece não determinada.
- **Banda de memória, false sharing, desbalanceamento: sem evidência.** O laço quase não acessa memória, a carga por iteração é uniforme, o OpenMP usa `reduction(+:dentro)` com blocos contíguos e o MPI usa blocos contíguos com `MPI_Reduce`. Nada nos dados indica esses efeitos.
- **Queda do OpenMP entre p = 2 e p = 4 (n = 100M): não explicada.** Eficiência 1,00 → 0,80, mas em n = 50M ela é 0,94 e em p = 6 volta a 0,86. A variação entre n sugere ruído do ambiente (WSL2) com apenas 3 repetições.

## 6. Laboratório
Pendente: executar as três versões na máquina do laboratório, com o mesmo protocolo de aquecimento e repetições, e salvar dados/figuras em destinos próprios. Registrar CPU, CPUs efetivas, versões, flags, binding e eventual sobrealocação. Conferir forte com 10M/50M/100M, fraca com 12,5M por worker e igualdade exata com o baseline. Comparar a curva completa e o MPI com um processo, sem pressupor que o fator observado no WSL será reproduzido. A demonstração ao vivo também permanece pendente.

## 7. Limitações
Três repetições com mediana, sem intervalo de confiança; coletas locais de máquinas diferentes, sem dados do laboratório; WSL2 e frequência do host podem introduzir variação. A escala fraca usa 12,5M pontos por worker. O tempo é interno à janela do protocolo e não mede o custo total de iniciar/finalizar `mpirun`. As curvas totais não isolam a duração das coletivas, false sharing ou banda de memória.

## 8. Conclusão
Na máquina do Gui, o OpenMP alcançou `S_seq=6,40` com oito threads em 100M e perdeu eficiência com 12 workers. O MPI alcançou `S_seq=3,93` e `S_1≈7,77` com oito processos. A divisão equilibrada, as reduções e os resultados exatos estão sustentados por código e testes. As causas de saturação e do fator próximo de 2 requerem controle experimental adicional; a análise registra as incertezas em vez de preenchê-las com hipóteses apresentadas como fatos. A conclusão definitiva de desempenho depende da máquina do laboratório.

## 9. Validação local da integração em 16/11/2026

Fontes desta rodada: [medições](../dados/integracao_local/medicoes.csv),
[ambiente e flags](../dados/integracao_local/ambiente.json),
[investigação MPI](../dados/integracao_local/investigacao_mpi.csv) e
[resumo da validação](../dados/integracao_local/validacao.json).
Os dados do Gui nas seções anteriores foram preservados. Este ambiente é
Ubuntu 26.04.1/WSL2, Intel Core i3-1315U, GCC 15.2, OpenMPI 5.0.10 e oito CPUs
lógicas visíveis. A coleta usa `-O2`, `OMP_DYNAMIC=FALSE`,
`OMP_PROC_BIND=FALSE` e `MPIRUN_EXTRA="--oversubscribe --bind-to none"`.
As 171 medições têm `OK`, com um aquecimento e três repetições por configuração.
Doze workers são sobrealocação. Não são dados de laboratório.

### Forte: 100 milhões

Todas as execuções produziram `pi=3.141499` e `dentro=78537472`.

| p | T seq (s) | T OpenMP (s) | T MPI (s) | S_seq OpenMP | S_seq MPI | E_seq OpenMP | E_seq MPI |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.347524 | 0.343419 | 0.336950 | 1.012 | 1.031 | 101.2% | 103.1% |
| 2 | 0.347524 | 0.179003 | 0.178076 | 1.941 | 1.952 | 97.1% | 97.6% |
| 4 | 0.347524 | 0.108688 | 0.107871 | 3.197 | 3.222 | 79.9% | 80.5% |
| 6 | 0.347524 | 0.087946 | 0.074306 | 3.952 | 4.677 | 65.9% | 77.9% |
| 8 | 0.347524 | 0.090551 | 0.058114 | 3.838 | 5.980 | 48.0% | 74.8% |
| 12 | 0.347524 | 0.094975 | 0.071445 | 3.659 | 4.864 | 30.5% | 40.5% |

O resumo gerado pelo analisador mantém as duas referências de speedup:

- mpi: `S_seq(8)=5.980` e `S_1(8)=5.798`.
- openmp: `S_seq(8)=3.838` e `S_1(8)=3.793`.

Nesta rodada, os tempos OpenMP com seis e oito threads ficaram próximos,
enquanto o MPI teve seu menor tempo com oito processos. Passar de oito para
12 workers piorou os tempos das duas versões. Isso é compatível com disputa
pelos recursos disponíveis; a coleta não isola frequência, SMT ou escalonamento
como causa. Os resultados não indicam alteração de desempenho do algoritmo
pelas correções do coletor: os fontes computacionais permaneceram idênticos.

Na entrada de 10M, a curva OpenMP desta rodada não foi monótona: seis e oito
threads tiveram ganhos menores que duas threads. Esses resultados foram
preservados. Tempos curtos, custos de início e variação do escalonamento/host
são hipóteses a controlar; três repetições não permitem isolar a causa.

### Fraca: 12,5 milhões por worker

| p | n | T OpenMP (s) | T MPI (s) | E fraca OpenMP | E fraca MPI |
|---:|---:|---:|---:|---:|---:|
| 1 | 12500000 | 0.042725 | 0.042422 | 100.0% | 100.0% |
| 2 | 25000000 | 0.044745 | 0.052825 | 95.5% | 80.3% |
| 4 | 50000000 | 0.060585 | 0.057052 | 70.5% | 74.4% |
| 6 | 75000000 | 0.095396 | 0.058116 | 44.8% | 73.0% |
| 8 | 100000000 | 0.098688 | 0.059759 | 43.3% | 71.0% |
| 12 | 150000000 | 0.122043 | 0.099906 | 35.0% | 42.5% |

A eficiência fraca cai nas configurações maiores; o trabalho por worker permanece
constante, mas criação/gestão de workers, redução, recursos compartilhados e
ruído do WSL continuam presentes. Esses custos não foram medidos separadamente.

### Investigação do fator 2 MPI

Foram executadas cinco configurações para cada um de 10M, 50M e 100M pontos:
sequencial livre, MPI sem binding, MPI com binding padrão, sequencial fixado
na CPU 0 e MPI com um processo fixado na mesma CPU 0. Cada configuração teve
um aquecimento descartado e três execuções válidas: **45 medições conferidas
com o gabarito**, todas `OK`. Os comandos estão no CSV específico.

O probe de afinidade confirmou que o binding padrão restringiu o processo MPI
às CPUs `[0,1]`, enquanto `--bind-to none` permitiu `[0,1,2,3,4,5,6,7]`.
O controle com `taskset -c 0` usou a mesma CPU para os dois programas.
As opções de binding são descritas na
[documentação do OpenMPI](https://docs.open-mpi.org/en/v5.0.x/man-openmpi/man1/mpirun.1.html).
As razões abaixo comparam medianas dentro desta investigação:

| n | MPI sem binding / seq. livre | MPI padrão / seq. livre | MPI CPU fixa / seq. CPU fixa |
|---:|---:|---:|---:|
| 10000000 | 1.103 | 1.016 | 1.031 |
| 50000000 | 1.037 | 1.003 | 0.991 |
| 100000000 | 0.990 | 0.987 | 1.017 |

Em 100M, as medianas foram 0.334133 s no sequencial
livre, 0.330785 s no MPI sem binding e
0.329643 s no MPI com binding padrão.
Na mesma CPU 0, foram 0.332795 s no sequencial e
0.338360 s no MPI. **O fator 2 não foi reproduzido.**

Esses controles mostram que a implementação MPI preservada pode apresentar
custo próximo ao sequencial com um processo neste ambiente. Eles não determinam
a causa do fator histórico em Ryzen/GCC 13.3/OpenMPI 4.1.6: hardware, versões e
condições diferem. Não há evidência para corrigir o algoritmo MPI por esse
motivo. A investigação histórica permanece aberta como limitação experimental;
no laboratório deve-se registrar binding/afinidade e repetir a comparação
controlada antes de atribuir uma causa.

### Reprodução das tabelas e figuras desta rodada

Na raiz, com C++17 e Matplotlib disponíveis, escolha diretórios de saída novos:

```bash
g++ -O2 -std=c++17 -o scripts/analisar scripts/analisar.cpp
./scripts/analisar dados/integracao_local/medicoes.csv dados/integracao_local/tabelas
python3 scripts/gerar_graficos.py --dados dados/integracao_local/tabelas --saida graficos/integracao_local
```

O analisador e o gerador foram executados na validação isolada; as cinco
tabelas/resumos e as seis figuras foram produzidas. As medianas e métricas foram
conferidas por cálculo independente. As imagens históricas do Gui não foram
substituídas. A validação e suas limitações estão registradas em
[validacao_integracao.md](validacao_integracao.md).
