# Análise do Algoritmo Sequencial — Estimativa de π por Monte Carlo

Código analisado: `baseline/02_montecarlo_pi.cpp` (IESB 2026/2 — CCO085 —
Prof. Rodrigo Gonçalves Pinto).

## 1. Funcionamento do método de Monte Carlo

O método estima π explorando a relação entre a área de um quarto de
círculo de raio 1 e a área do quadrado `[0,1) x [0,1)` que o contém.
Nesse quadrado unitário, a área do quarto de círculo é π/4 e a área do
quadrado é 1; logo, a probabilidade de um ponto sorteado uniformemente
nesse quadrado cair dentro do quarto de círculo é π/4. Sorteando `n`
pontos `(x, y)` e contando quantos satisfazem `x² + y² ≤ 1`, a
proporção `dentro / n` converge para π/4 conforme `n` cresce,
permitindo estimar π como `4 · dentro / n`. É um método estocástico:
o erro da estimativa diminui com `n`, mas nunca é eliminado — apenas
a variância cai.

## 2. Fluxo do código sequencial

1. **Leitura da entrada**: `n` é lido de `argv[1]` (padrão
   `50.000.000` se nenhum argumento for passado).
2. **Inicialização**: a semente do gerador é fixada em
   `s = 88172645463325252ULL` e o contador `dentro` é zerado.
3. **Marca de tempo inicial** (`t0 = agora()`), imediatamente antes do
   laço — ou seja, o próprio baseline já isola o tempo do laço
   principal do resto do programa.
4. **Laço principal**: repetido `n` vezes, gera `x` e `y`, testa
   `x*x + y*y <= 1.0` e incrementa `dentro` quando verdadeiro.
5. **Cálculo final**: `pi = 4.0 * dentro / n`.
6. **Marca de tempo final** (`t1 = agora()`), imediatamente após o
   cálculo de π. Portanto, a janela `t0`–`t1` inclui o laço e esse
   cálculo final de custo constante.
7. **Saída**: imprime `n`, `pi`, `dentro` e o tempo do laço
   (`t1 - t0`) no formato `n=... pi=... dentro=... tempo=... s`.

## 3. Geração dos pontos (x, y)

O gerador não usa `rand()`/`srand()`, e sim um **xorshift64**
(`xorshift(s)`): a cada chamada, a função aplica três deslocamentos
XOR sobre o estado de 64 bits `s` e retorna o novo estado. Cada
coordenada é obtida descartando os 11 bits menos significativos do
resultado (`>> 11`, restando 53 bits) e multiplicando por
`1 / 2^53`, o que produz um `double` uniformemente distribuído em
`[0, 1)` com toda a precisão de mantissa disponível em ponto
flutuante de 64 bits. `x` e `y` usam chamadas consecutivas do mesmo
gerador, portanto são sequenciais e dependentes do mesmo estado
interno `s`.

Um detalhe relevante indicado no próprio comentário do código: esse
xorshift é de estado único e sequencial — em uma versão paralela
(OpenMP/MPI, prevista para os próximos marcos), cada thread/processo
precisará de seu próprio gerador com semente independente, já que o
estado `s` não pode ser compartilhado sem sincronização.

## 4. Teste `x*x + y*y <= 1.0`

Verifica se o ponto sorteado está dentro (ou sobre a borda) do
quarto de círculo de raio 1 centrado na origem. `x*x + y*y` é o
quadrado da distância do ponto à origem; se esse valor for menor ou
igual a 1, o ponto está dentro do círculo. Cada teste verdadeiro
incrementa `dentro`.

## 5. Cálculo final da estimativa de π

Como a razão entre a área do quarto de círculo e a do quadrado
unitário é π/4, `dentro / n` aproxima π/4, e multiplicar por 4
fornece a estimativa: `pi = 4.0 * (double)dentro / (double)n`. Esse
cálculo ocorre uma única vez, após o laço, com custo constante e antes
da marca de tempo final `t1`; portanto, ele está incluído na janela
medida internamente pelo programa, embora seu custo seja desprezível
em relação ao laço.

## 6. Complexidade de tempo

O laço principal executa exatamente `n` iterações, cada uma com um
número constante de operações (duas chamadas a `xorshift`, duas
multiplicações, uma soma, uma comparação e, eventualmente, um
incremento). Não há laços aninhados nem crescimento de trabalho por
iteração. Logo, a complexidade de tempo é:

**O(n)**

## 7. Complexidade de memória

O programa usa um número fixo de variáveis escalares (`n`, `s`,
`dentro`, `x`, `y`, `pi`, `t0`, `t1`), independentemente do valor de
`n`. Não há alocação de estruturas cujo tamanho cresça com `n`.
Logo, a complexidade de memória é:

**O(1)**

## 8. Hotspot inicial (candidato)

O laço principal concentra toda a geração de números aleatórios, o
teste geométrico e a atualização do contador, sendo o único trecho
cujo custo cresce com `n` — inicialização, cálculo final e impressão
têm custo constante. É esperado, portanto, que o laço domine o tempo
total à medida que `n` aumenta. Essa hipótese é reforçada pelo
próprio autor do baseline, que já isola o tempo do laço com
`clock_gettime` (variável `tempo` na saída) separadamente do restante
do programa — mas a confirmação definitiva, incluindo o percentual
exato do tempo total, é feita experimentalmente em
`secoes/perfilamento_amdahl.md`.
