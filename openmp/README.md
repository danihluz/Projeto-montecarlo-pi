# Estimativa de π com OpenMP

## Objetivo

Paralelizar a estimativa de π por Monte Carlo mantendo exatamente os mesmos
pontos, a contagem `dentro` e o valor de `pi` do programa sequencial
`baseline/02_montecarlo_pi.cpp`, para a mesma entrada e ambiente de compilação.

## Estratégia de paralelização

Somente o processamento das amostras é paralelo. Para uma equipe de `p`
threads, cada thread `t` recebe um intervalo contíguo, definido por:

```text
q = n / p
r = n % p
inicio(t) = t*q + min(t, r)
tamanho(t) = q + (t < r ? 1 : 0)
fim(t) = inicio(t) + tamanho(t)
```

Os primeiros `r` blocos recebem uma amostra adicional. Os intervalos cobrem
`[0, n)` sem lacunas ou sobreposições; blocos vazios não acessam o gerador.
A divisão usa o tamanho real da equipe, obtido por `omp_get_num_threads()`.

A região `parallel reduction(+:dentro)` com blocos manuais mantém a distribuição
estática e permite posicionar o gerador uma única vez por thread. Essa escolha
explicita os limites necessários ao salto, sem depender da distribuição interna
de `parallel for schedule(static)`.

## Sincronização e condições de corrida

A redução fornece um contador privado para cada thread e combina as contagens
ao final da região paralela. Isso evita a condição de corrida de um incremento
compartilhado e a contenção de `critical` ou `atomic` por amostra.

O estado do gerador, as coordenadas e os limites do bloco são privados. A
semente-base e a tabela de saltos são compartilhadas somente para leitura.
`default(none)` explicita o compartilhamento. O cálculo final de π ocorre
depois da sincronização e da redução.

## Preservação do gerador por jump-ahead

O xorshift original é mantido: estado `uint64_t`, deslocamentos 13, 7 e 17,
semente `88172645463325252ULL` e duas chamadas por ponto. Permanecem a conversão
`(estado >> 11) * (1.0 / 9007199254740992.0)`, o teste
`x*x + y*y <= 1.0` e a expressão `4.0 * (double)dentro / (double)n`.

XOR e deslocamentos são operações lineares sobre GF(2). A transição do gerador
é representada por uma matriz `T` de 64 bits; suas colunas são as imagens dos
vetores da base. Por quadrados sucessivos, calculam-se `T`, `T²`, `T⁴`, etc.
A decomposição binária do deslocamento seleciona as potências necessárias.

Uma thread cujo bloco começa no ponto `inicio` recebe o estado
`T^(2*inicio)(semente)`. Suas próximas duas chamadas coincidem com as chamadas
correspondentes do sequencial. Não se usam sementes arbitrárias por thread nem
avanço iterativo proporcional ao tamanho do prefixo.

A tabela ocupa 32 KiB, é preparada uma vez e fica imutável durante a execução
paralela. A preparação custa `O(64² log n)` e cada posicionamento,
`O(64 log n)`. A conversão para `uint64_t` precede a multiplicação por dois;
a partição evita o produto intermediário `n*tid` em tipo com sinal.

## Contrato de entrada e saída

- `argv[1]` informa o número total de pontos, lido com `atol`, como no baseline.
- Sem argumento, são utilizadas 50.000.000 de amostras.
- `OMP_NUM_THREADS` solicita a quantidade de threads; o código não a fixa.
- A saída contém exatamente uma linha, com seis casas decimais em `pi` e `tempo`:

```text
n=<n>  pi=<pi>  dentro=<dentro>  tempo=<segundos> s
```

O caminho do executável e o formato da saída atendem ao contrato do coletor do
projeto. Entradas não positivas mantêm o comportamento do baseline, incluindo
`nan` para zero, e ficam fora das medições de desempenho.

O tempo usa `clock_gettime(CLOCK_MONOTONIC)` e inclui preparação do jump-ahead,
posicionamento dos estados, criação e sincronização das threads, processamento,
redução e cálculo final de π. A leitura da entrada e a impressão ficam fora.

## Compilação

Requisitos: G++ com OpenMP e suporte a C++11 ou posterior; Python 3.9 ou
posterior para executar o verificador. Na raiz do repositório:

```bash
mkdir -p openmp/.build
g++ -O2 -fopenmp -o openmp/02_montecarlo_pi_omp openmp/02_montecarlo_pi_openmp.cpp
g++ -O2 -o openmp/.build/baseline_original baseline/02_montecarlo_pi.cpp
g++ -O2 -fopenmp -o openmp/.build/testar_jump openmp/testar_jump.cpp
```

O baseline é compilado sem alterar sua fonte. No Windows/MSYS2, os executáveis
recebem a extensão `.exe`; no PowerShell, use `New-Item -ItemType Directory
-Path openmp/.build -Force` para criar o diretório e `python` no lugar de
`python3` nos comandos abaixo.

## Execução

Exemplos para um shell Linux:

```bash
OMP_NUM_THREADS=1 ./openmp/02_montecarlo_pi_omp 50000000
OMP_NUM_THREADS=4 ./openmp/02_montecarlo_pi_omp 50000000
OMP_NUM_THREADS=12 ./openmp/02_montecarlo_pi_omp 50000000
```

No PowerShell, a configuração equivalente é:

```powershell
$env:OMP_NUM_THREADS='4'
.\openmp\02_montecarlo_pi_omp.exe 50000000
```

## Validação

Após compilar os três executáveis:

```bash
./openmp/.build/testar_jump
python3 openmp/testar_verificador.py
python3 openmp/verificar.py
```

`testar_jump.cpp` compara saltos com avanços iterativos e verifica composição,
índices de 64 bits e cobertura dos blocos, inclusive perto de `LONG_MAX`.
`testar_verificador.py` verifica a proteção contra sobrescrita dos registros.

O verificador compara `n`, `dentro` e `pi` com execuções do baseline original.
Inclui entradas pequenas, não divisíveis, padrão e de borda; repetições com
1, 2, 4, 6, 8 e 12 threads, conforme os recursos disponíveis; e casos com equipe
limitada ou ajuste dinâmico. Os sete tamanhos do gabarito são conferidos também
contra o sequencial. A referência está em `gabarito_referencia.csv`, obtida do
[gabarito do projeto](https://github.com/danihluz/Projeto-montecarlo-pi/blob/e0917954201eeb854f094f36b9f94f41a3dd81a1/dados/gabarito.csv).

Os registros são gerados em `openmp/.build/resultados/`, ignorado pelo Git.
O destino precisa ser inexistente para preservar rodadas anteriores. Para
repetir a validação, escolha outro nome:

```bash
python3 openmp/verificar.py --saida openmp/.build/validacao02
```

A coleta diagnóstica opcional segue um aquecimento descartado e três execuções
válidas por configuração, utilizando a mediana:

```bash
python3 openmp/verificar.py --medir --saida openmp/.build/medicao01
```

A escala forte usa 10M, 50M e 100M de amostras; a fraca usa 12,5M por thread.
O resumo diferencia `S_seq(p)=T_seq(n)/T_omp(n,p)` e `E_seq(p)=S_seq(p)/p`
do speedup relativo ao OpenMP com uma thread. A eficiência fraca compara
`T_omp(12,5M,1)` com `T_omp(12,5M*p,p)`.

## Limitações e validação final

A implementação compilou e os testes passaram em Windows/MSYS2, incluindo
374 comparações com o baseline nas seis quantidades de threads. Esses testes
não substituem a validação definitiva no Linux da disciplina, as medições
finais de escalabilidade e a demonstração ao vivo.

No Windows/UCRT, `long` tem 32 bits; no Linux x86-64, tem 64 bits. Entradas
além do limite do tipo não são comparáveis entre os ambientes. Os testes
próximos do limite de 64 bits de `long` devem ser repetidos no Linux.

Antes das medições finais, registrar compilador, CPU e limites efetivos de
threads, afinidade e quota do contêiner. A quantidade de threads criada não
garante CPUs dedicadas. Em versões antigas do Python, a contagem de CPUs usada
pelo verificador pode não refletir restrições de afinidade ou quota.

A estrutura evita compartilhamento mutável do gerador e usa redução para a
contagem; os testes de repetibilidade não substituem um detector de corridas.
Não foi executado ThreadSanitizer. O relógio POSIX segue o baseline, e o suporte
verificado no Windows corresponde ao MSYS2, sem validação para MSVC.
