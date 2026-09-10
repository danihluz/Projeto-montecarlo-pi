# Perfilamento e Lei de Amdahl

## Metodologia do perfilamento

Foi criada uma cópia instrumentada do baseline,
`baseline/02_montecarlo_pi_perfilamento.cpp`, **sem nenhuma alteração
na lógica do algoritmo** (mesmo gerador xorshift64, mesma semente,
mesmo teste `x*x+y*y<=1`, mesmo cálculo de π). O baseline original já
media internamente o tempo do laço principal com
`clock_gettime(CLOCK_MONOTONIC)` (variável `tempo` da saída); a única
adição foram duas marcas de tempo extras, uma no início de `main` e
outra logo após o laço/cálculo (antes do `printf`), para obter o
tempo **total** do programa. A diferença entre o tempo total e o
tempo do laço fornece o tempo gasto em "outros trechos" (leitura de
`argv`, inicialização de variáveis e do estado do gerador, cálculo
final de π).

Não foi necessário fatiar o laço principal em pedaços menores para
identificar o hotspot — os dois pontos de medição (laço vs. resto do
programa) já são suficientes para isolar claramente onde o tempo é
gasto. Evitou-se, assim, instrumentação adicional dentro do laço, que
acrescentaria overhead de chamadas a `clock_gettime` a cada iteração
(ou a cada bloco de iterações) sem necessidade.

**Protocolo de medição**: para cada um dos três tamanhos de entrada
(10.000.000, 50.000.000, 100.000.000), 1 execução de aquecimento
(descartada) seguida de 3 execuções válidas, com o script
`scripts/medir_perfilamento.sh`, que compila com `g++ -O2`, extrai os
tempos de cada execução (linha `PERFIL,...` em stderr) e calcula a
mediana de `tempo_total`, `tempo_laco` e `tempo_outros`.

## Verificação de overhead da instrumentação

Comparando a mediana do `tempo` do baseline original (Issue #2) com a
mediana do `tempo_laco` da versão instrumentada, para o mesmo `n`:

| n | tempo (baseline original) | tempo_laco (instrumentado) | diferença |
|---|---|---|---|
| 10.000.000 | 0.039873 s | 0.037520 s | -0.002353 s |
| 50.000.000 | 0.192925 s | 0.188754 s | -0.004171 s |
| 100.000.000 | 0.382950 s | 0.375477 s | -0.007473 s |

As diferenças são pequenas e, na verdade, o tempo medido na versão
instrumentada ficou até um pouco *menor* em todos os casos — dentro
da variação normal de execução para execução (ruído do sistema,
scheduler, cache), e não um efeito sistemático da instrumentação em
si, já que as únicas linhas adicionadas ficam **fora** da região
medida pelo `t0`/`t1` original. Isso confirma que a instrumentação
introduzida não distorceu a medição do laço principal.

## Tabela de percentual por trecho

Dados completos em `dados/perfilamento.csv` (medianas de 3 execuções
válidas por `n`, após 1 execução de aquecimento descartada):

| n | trecho | tempo (s) | percentual |
|---|---|---|---|
| 10.000.000 | laço principal | 0.037520 | 99,97% |
| 10.000.000 | outros trechos | 0.000007 | 0,02% |
| 10.000.000 | total | 0.037528 | 100% |
| 50.000.000 | laço principal | 0.188754 | 99,99% |
| 50.000.000 | outros trechos | 0.000007 | ~0% |
| 50.000.000 | total | 0.188763 | 100% |
| 100.000.000 | laço principal | 0.375477 | 99,99% |
| 100.000.000 | outros trechos | 0.000007 | ~0% |
| 100.000.000 | total | 0.375485 | 100% |

## Hotspot — evidência

O laço principal concentra **entre 99,97% e 99,99%** do tempo total
de execução nos três tamanhos testados, confirmando experimentalmente
a hipótese levantada na análise do algoritmo
(`secoes/algoritmo_sequencial.md`): é o único trecho cujo custo cresce
com `n` (inicialização e cálculo final têm custo O(1) e, na prática,
consomem microssegundos, enquanto o laço consome de dezenas a
centenas de milissegundos). O hotspot do programa é, portanto, **o
laço principal** (geração de `(x,y)` + teste geométrico + contagem).

## Lei de Amdahl

A fração paralelizável `P` foi calculada a partir dos tempos medidos
para n = 100.000.000 (maior entrada, medição mais estável em relação
à resolução do timer):

```
P = tempo_laco / tempo_total = 0.375477 / 0.375485 ≈ 0.99998
```

Aplicando `S(p) = 1 / ((1-P) + P/p)`:

| p | S(p) |
|---|---|
| 2 | 1,9999 |
| 4 | 3,9997 |
| 8 | 7,9988 |

Limite teórico:

```
Smax = 1 / (1 - P) ≈ 46.935
```

## Interpretação

O valor de `P` obtido é extremamente próximo de 1, refletindo o fato
de que, nesse baseline sequencial, praticamente todo o tempo de
execução está concentrado no laço principal — um algoritmo
"embaraçosamente paralelo" (*embarrassingly parallel*), como o
próprio comentário no cabeçalho do código já indicava. Isso faz os
speedups teóricos S(2), S(4) e S(8) ficarem muito próximos do ideal
linear (2x, 4x, 8x).

É importante notar, porém, uma limitação desse cálculo: o
`tempo_outros` medido (poucos microssegundos) está no limite da
resolução prática do timer e da variação normal de execução do
sistema — ou seja, `P ≈ 0,99998` reflete a fração sequencial *deste
programa sequencial específico*, e não necessariamente a fração
sequencial que uma implementação paralela real teria. Ao paralelizar
de fato (com OpenMP ou MPI, previsto para os próximos marcos), surgem
custos que não existem na versão sequencial e que não são capturados
por este perfilamento: criação/sincronização de threads ou processos,
necessidade de um gerador de números aleatórios independente por
thread (mencionada no comentário do próprio baseline), contenção de
cache/memória entre unidades de execução, e a redução dos contadores
parciais `dentro` de cada thread em um valor final. Por isso, o
speedup real observado após a paralelização tende a ficar abaixo do
previsto por `S(p)` e, principalmente, muito abaixo do limite teórico
`Smax`, que é dominado por um `1-P` tão pequeno que se torna pouco
representativo dos custos reais de paralelização.