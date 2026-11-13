# MPI — Marco 2 — Danielly de Sousa Luz

Esta implementação distribui entre processos os mesmos pontos produzidos por
`baseline/02_montecarlo_pi.cpp`. Preserva o gerador, a semente, a conversão para
`double`, o teste `x*x + y*y <= 1.0` e o cálculo final de π do professor.
O baseline e os arquivos dos demais integrantes não são modificados.

## Compilação e execução

Em Linux, com compilador C++ e MPI disponíveis, execute na raiz do repositório:

```bash
make -C mpi
mpirun -np 4 mpi/02_montecarlo_pi_mpi 50000000
```

Compilação direta equivalente:

```bash
mpic++ -O2 -o mpi/02_montecarlo_pi_mpi mpi/02_montecarlo_pi_mpi.cpp
```

O único argumento do programa é o total de pontos; se omitido, o padrão é
50.000.000, como no baseline. O número de processos é definido pelo executor
MPI. Para `n <= 0`, todos os processos finalizam com erro e somente o rank 0
escreve a mensagem em stderr.

Somente o rank 0 imprime o resultado, neste formato exato:

```text
n=<n>  pi=<seis casas>  dentro=<inteiro>  tempo=<seis casas> s
```

O executável tem o caminho esperado pelo coletor do PR #14. Não foi necessário
adicionar um alvo ao Makefile compartilhado.

## Divisão e reunião do trabalho

`MPI_Init` inicia o ambiente MPI. `MPI_Comm_rank` fornece a identificação de
cada processo, de 0 a `p-1`; `MPI_Comm_size` fornece `p`. O rank 0 interpreta
a entrada, e `MPI_Bcast`, com `MPI_LONG`, envia `n` aos demais processos.

Cada processo calcula seu intervalo contíguo, sem enviar pontos pela rede:

```text
base       = n / p
resto      = n % p
quantidade = base + (rank < resto ? 1 : 0)
inicio     = rank * base + min(rank, resto)
intervalo  = [inicio, inicio + quantidade)
```

Os primeiros `resto` processos recebem um ponto a mais. O fim de um bloco é
o início do próximo, o primeiro começa em zero e o último termina em `n`.
Portanto, não há lacunas nem sobreposições. Se `p > n`, alguns blocos ficam
vazios e continuam participando das operações coletivas.

Por exemplo, para `n=10` e `p=3`, os blocos são `[0,4)`, `[4,7)` e `[7,10)`.
Cada processo mantém sua própria contagem. `MPI_Reduce`, com `MPI_SUM` e
`MPI_LONG`, soma as contagens no rank 0. A soma inteira independe da ordem
de reunião dos processos. A raiz calcula `4.0 * dentro_global / n` e imprime.
Todos chamam `MPI_Finalize` para encerrar o ambiente.

## Por que o jump-ahead preserva exatamente a sequência

Chame de `T` uma chamada ao xorshift original e de `s0` sua semente fixa,
`88172645463325252ULL`. O ponto de índice `i`, começando em zero, usa os estados
`T^(2i+1)(s0)` para `x` e `T^(2i+2)(s0)` para `y`. Logo, antes do primeiro
ponto de um bloco, seu estado precisa ser `T^(2*inicio)(s0)`.

Sobre vetores de 64 bits, cada deslocamento e XOR é linear em GF(2): a soma
nesse espaço é o XOR. Assim, `T(a XOR b) = T(a) XOR T(b)`. A transformação
inteira é representada por 64 palavras de 64 bits: a coluna `j` é `T(1<<j)`.
Aplicar a transformação significa combinar por XOR as colunas dos bits
presentes no estado.

`avancar` usa exponenciação por quadrados. Começa com `T`; em cada etapa,
aplica a potência quando o bit correspondente do deslocamento está ligado
e obtém a próxima potência compondo a transformação consigo mesma:
`T`, `T²`, `T⁴`, `T⁸`, etc. Isso calcula exatamente `T^k(s0)` usando somente
operações inteiras. Não é uma aproximação nem uma nova semente aleatória.

O salto de cada rank é para `k=2*inicio`. Depois dele, o laço executa as duas
chamadas originais por ponto. Consequentemente, cada coordenada e cada teste
geométrico correspondem ao baseline. No exemplo `n=10, p=3`, os estados
iniciais estão nas transições 0, 8 e 14 da mesma sequência.

O número de operações de preparação cresce com `log(k)` para uma largura fixa
de 64 bits. Não é preciso gerar ou descartar os `2*inicio` números anteriores,
nem passar todos os pontos pelo rank 0. Depois da preparação, os ranks
executam seus laços simultaneamente e não trocam mensagens por ponto.

## Janela de tempo e custos

A medição segue o protocolo do PR #14:

1. Todos chamam `MPI_Barrier` antes da marca inicial.
2. `MPI_Wtime()` marca o início em cada rank.
3. São medidos a divisão, o jump-ahead, o laço local, a redução das contagens
   e, na raiz, o cálculo de π.
4. Cada rank calcula seu intervalo de tempo com o próprio relógio.
5. Uma segunda redução, com `MPI_MAX`, escolhe o maior intervalo para a saída.

Não se subtraem relógios de ranks diferentes. A redução usada para comunicar
os tempos e o `printf` ficam fora dos intervalos já medidos. `MPI_Init`, a
distribuição da entrada, a barreira inicial e `MPI_Finalize` também ficam fora.
O tempo impresso não é o tempo total do comando `mpirun`.

Há uma transmissão de entrada, uma barreira e duas reduções de escalares.
Não há comunicação durante o laço. O custo do jump-ahead, a espera pelo rank
mais lento, as coletivas e a disputa por CPU podem reduzir o speedup, sobretudo
para entradas pequenas. A diferença entre as cargas é de no máximo um ponto.
Usar mais processos que CPUs não acrescenta capacidade física de cálculo.

## Validação reproduzível

```bash
make -C mpi testar-jump
python3 mpi/testar.py
```

O primeiro teste usa `#include` do arquivo original do professor, renomeando
somente `main` no pré-processamento do teste. Dessa forma, a referência é a
própria função `xorshift` do baseline, sem editar esse arquivo.

São comparados estados nas posições pequenas, potências de dois e seus
vizinhos, posições grandes até 300.000.000 transições e limites dos blocos
dos tamanhos do protocolo. A referência percorre sequencialmente o gerador.
São usadas a semente do professor e quatro estados adicionais, incluindo zero
e estados com bits altos. Também são verificados a cobertura dos blocos, seu
balanceamento e as duas coordenadas de cada ponto das entradas pequenas.

O teste Python requer Python 3 com biblioteca padrão, acesso à internet para
ler o commit fixado do PR e MPI no `PATH`. Ele:

- Compila o baseline original para `mpi/.testes/`, sem substituir o executável
  previamente existente em `baseline/`.
- Compara exatamente `dentro` e `pi`, verifica a linha inteira de saída e
  exige stderr vazio nas execuções válidas.
- Usa entradas pequenas, divisões com resto, `p > n`, uma entrada de
  10.000.003 pontos e todos os sete tamanhos do gabarito.
- Confere o argumento omitido e a rejeição de zero e valores negativos.
- No MPICH/Hydra, usa a identificação de rank do executor para confirmar
  que a única linha vem do rank 0.
- Baixa cópias intactas de `coletar.sh`, `analisar.cpp`, `gabarito.csv` e
  `protocolo_medicao.md` do commit `e0917954201eeb854f094f36b9f94f41a3dd81a1`
  para `mpi/.testes/pr14/` e registra seus hashes SHA-256.
- Executa o coletor original com `VERSOES="sequencial mpi"`, um aquecimento
  e três repetições válidas; depois executa o analisador original.
- Salva as comparações, medições, tabelas, caracterização e logs em
  `mpi/resultados/`. Uma divergência ou falha causa retorno diferente de zero.

O coletor original fixa `p=1,2,4,6,8,12`. No ambiente usado, há oito CPUs
lógicas disponíveis: os testes com 12 processos representam sobrealocação e
servem para verificar compatibilidade nessa condição. Seus tempos são reais,
mas precisam dessa ressalva em qualquer comparação de desempenho.

## Ambiente local usado nos testes

Os detalhes reais da máquina, compiladores e MPI estão em
`resultados/maquina.txt`; os comandos e saídas estão em
`resultados/validacao.log`.

Foi usado Ubuntu/WSL, com MPICH 4.3.2 e GCC 15.2. Como MPI não estava instalado,
foram baixados sete pacotes oficiais dos repositórios configurados do Ubuntu
e extraídos com `dpkg-deb -x` em `mpi/.ambiente/raiz/`. Nenhum pacote foi
instalado no sistema, nenhum `sudo` foi usado e nenhuma configuração global
foi alterada. O download somou aproximadamente 9,5 MB.

Pacotes extraídos: `mpich`, `libmpich12`, `libmpich-dev`, `libhwloc15`,
`libucx0`, `libnuma1` e `libgfortran5`. Essa extração local não equivale a uma
instalação completa de desenvolvimento MPI/Fortran: fornece o necessário para
compilar e executar estes programas C++ no ambiente verificado.

Nesta cópia de trabalho, a ativação temporária é:

```bash
source mpi/.ambiente/ativar.sh
make -C mpi
python3 mpi/testar.py
```

Ela ajusta somente o ambiente do shell atual (`PATH`, `LD_LIBRARY_PATH` e o
launcher local `HYDRA_LAUNCHER=fork`). Os adaptadores locais de `mpic++` e
`mpirun` apontam para os arquivos extraídos. Essa pasta é ignorada pelo Git.
Em uma máquina com MPI instalado normalmente, a ativação não é necessária.

## Integração com o trabalho do Gui

A branch parte da `main` anterior ao PR #14. Não houve merge, push ou abertura
de PR. Todos os novos arquivos versionados estão em `mpi/`.

O PR #14 ainda precisa passar pela revisão e integração do grupo. O coletor
espera que o executável MPI já esteja compilado; `make -C mpi` satisfaz isso.
Depois da integração autorizada do PR, os comandos compatíveis são:

```bash
make -C mpi
VERSOES="sequencial mpi" OUT=mpi/resultados/medicoes.csv bash scripts/coletar.sh todas
g++ -O2 -std=c++17 -o scripts/analisar scripts/analisar.cpp
./scripts/analisar mpi/resultados/medicoes.csv mpi/resultados
```

O baseline também deve estar compilado e `dados/gabarito.csv` deve existir com
finais de linha LF. As cópias isoladas dos testes preservam os bytes do PR e
evitam o problema de CRLF observado no Windows. A configuração local de
atributos em `mpi/` não altera os arquivos compartilhados.

Os speedups comparam tempos medidos nesta mesma máquina. Os resultados do
Gui obtidos em outra máquina não são usados como denominador. Ainda faltam
as medições finais no laboratório, com registro de seu ambiente, e a coleta
conjunta com a implementação OpenMP do Heitor. O PDF original do enunciado
não estava disponível; a implementação segue o baseline, as instruções da
Danielly e o contrato do PR inspecionado.
