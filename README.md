# Estimativa de π por Monte Carlo

Projeto de Programação Paralela (CCO085), IESB, 2026/2. O objetivo é comparar o
baseline sequencial fornecido pelo professor Rodrigo Gonçalves Pinto com versões
OpenMP e MPI que reproduzem exatamente seus valores de `dentro` e `pi`.

Integrantes: Guilherme Ferreira de Souza, Heitor dos Santos Ribeiro e Danielly de
Sousa Luz. As contribuições estão em [AUTORES.md](AUTORES.md).

## Estrutura

- `baseline/`: original do professor, preservado, e cópia instrumentada para perfilamento;
- `openmp/`: implementação por threads, jump-ahead e testes de Heitor;
- `mpi/`: implementação por processos, jump-ahead, testes e registros de Danielly;
- `scripts/`: gabarito, coleta, regressões do coletor, análise, Amdahl e gráficos;
- `dados/`: medições históricas do Gui, gabarito e tabelas;
- `dados/integracao_local/`: nova coleta local e investigação MPI, separadas das anteriores;
- `graficos/`: seis gráficos dos dados históricos do Gui;
- `secoes/`: análises, planos do Marco 1 e registro da validação integrada;
- `Makefile`: compilação das três versões e do perfilamento opcional.

## Dependências e ambiente

O ambiente de referência é Linux com G++, GNU Make, OpenMP e OpenMPI. Os
programas usam `-O2`; OpenMP acrescenta `-fopenmp`. A análise em C++ requer C++17.
Os testes requerem Python 3.9 ou posterior e usam a biblioteca padrão. Somente a exportação dos gráficos
requer Python 3 com Matplotlib.

Em Ubuntu, se as ferramentas não estiverem instaladas (como root, omita `sudo`):

```bash
sudo apt-get update
sudo apt-get install build-essential openmpi-bin libopenmpi-dev python3
# Opcional, para gerar as figuras:
sudo apt-get install python3-matplotlib
```

No ambiente da disciplina, abra a pasta `ambiente_pp` no Dev Container fornecido
pelo professor e execute os comandos na raiz deste projeto, dentro de `codigos/`.
A configuração genérica `.devcontainer/` deste repositório é distinta e não
declara explicitamente os pacotes MPI. Confira `g++ --version`,
`mpic++ --version` e `mpirun --version` antes de usar outro contêiner.

Chame os scripts Bash com `bash`, como nos exemplos. O coletor aceita o gabarito
com LF ou CRLF. As medições finais e a demonstração no laboratório estão pendentes.

## Compilação

Na raiz do repositório:

```bash
make
```

O Makefile gera os caminhos esperados pelo coletor:

| Alvo individual | Executável | Compilação |
|---|---|---|
| `make baseline` | `baseline/02_montecarlo_pi` | `g++ -O2` |
| `make openmp` | `openmp/02_montecarlo_pi_omp` | `g++ -O2 -fopenmp` |
| `make mpi` | `mpi/02_montecarlo_pi_mpi` | `mpic++ -O2` |

`make perfilamento` mantém o alvo da cópia instrumentada. `make clean` remove
somente os quatro executáveis definidos no Makefile, preservando dados e figuras.
É possível selecionar ferramentas por linha de comando: `make MPICXX=mpicxx`.

## Execução e contrato

```bash
./baseline/02_montecarlo_pi 50000000
OMP_NUM_THREADS=4 ./openmp/02_montecarlo_pi_omp 50000000
mpirun -np 4 ./mpi/02_montecarlo_pi_mpi 50000000
```

`argv[1]` informa o total de pontos `n`; o domínio de comparação é **`n > 0`**.
Sem argumento, as três versões usam 50 milhões. Threads são definidas por
`OMP_NUM_THREADS`, e processos por `mpirun -np`. A saída é uma única linha:

```text
n=<n>  pi=<seis casas>  dentro=<inteiro>  tempo=<seis casas> s
```

Para 50 milhões, o gabarito é `pi=3.141429`, `dentro=39267859`; o tempo varia.
O gerador, a semente e o teste geométrico são preservados. OpenMP/MPI posicionam
estados privados por jump-ahead na mesma sequência. Para entradas não positivas,
MPI retorna erro; sequencial e OpenMP conservam o comportamento do baseline.
Essas entradas não participam dos benchmarks.

## Testes de corretude

```bash
make
python3 scripts/testar_coletor.py -v
mkdir -p openmp/.build
g++ -O2 -fopenmp -o openmp/.build/testar_jump openmp/testar_jump.cpp
python3 openmp/testar_verificador.py
python3 openmp/verificar.py --seq baseline/02_montecarlo_pi
make -C mpi testar-jump
```

O teste do coletor usa saídas sintéticas em diretórios temporários: verifica
LF/CRLF, `n`, `pi` e `dentro` incorretos, saída duplicada, falha do programa e
descarte do aquecimento. Suas saídas não são medições experimentais.

O verificador OpenMP compara execuções reais com o baseline, incluindo
repetibilidade e equipes ajustadas. Para repetir, escolha um destino novo:
`python3 openmp/verificar.py --seq baseline/02_montecarlo_pi --saida openmp/.build/rodada02`.

O teste completo `mpi/testar.py` **reescreve `mpi/resultados/`** e requer internet
para baixar quatro arquivos de um commit histórico fixado do Gui. Execute-o em
uma cópia isolada. Com as alterações já commitadas, uma opção é:

```bash
teste_mpi=$(mktemp -d)
git archive HEAD | tar -x -C "$teste_mpi"
(cd "$teste_mpi" && MPIRUN_EXTRA="--oversubscribe --bind-to none" python3 mpi/testar.py)
printf 'Resultados MPI da rodada: %s/mpi/resultados\n' "$teste_mpi"
```

Esse teste verifica MPI com o coletor histórico; o coletor atual é exercitado
pelas regressões acima e pela coleta conjunta. Mais detalhes:
[openmp/README.md](openmp/README.md) e [mpi/README.md](mpi/README.md).

## Coleta, análise e gráficos

O gabarito versionado está em `dados/gabarito.csv`. Para regenerá-lo, use
`bash scripts/gerar_gabarito.sh`; o comando substitui esse arquivo.

Escolha **um nome novo por máquina/rodada**. Coletor, analisador e gerador de
gráficos substituem destinos existentes. Exemplo completo:

```bash
make
mkdir -p dados/nova_coleta
OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE \
MPIRUN_EXTRA="--oversubscribe --bind-to none" \
OUT=dados/nova_coleta/medicoes.csv bash scripts/coletar.sh todas
g++ -O2 -std=c++17 -o scripts/analisar scripts/analisar.cpp
./scripts/analisar dados/nova_coleta/medicoes.csv dados/nova_coleta
python3 scripts/gerar_graficos.py --dados dados/nova_coleta --saida graficos/nova_coleta
```

`forte` ou `fraca` podem substituir `todas`. `VERSOES="sequencial openmp mpi"`
seleciona as versões sem alterar o formato CSV. O coletor exige uma linha de
resultado por execução, compara `n`, `pi` e `dentro` com a referência e registra
`DIVERGENTE` antes de encerrar com erro se houver incompatibilidade. Não analise
uma coleta interrompida como se fosse completa.

O protocolo usa um aquecimento descartado e três repetições válidas por
configuração. A escala forte fixa 10M, 50M e 100M pontos; a fraca usa 12,5M por
worker. Os workers são 1, 2, 4, 6, 8 e 12. A coleta completa tem **171 linhas de
medição e 57 configurações**. `--oversubscribe` permite ultrapassar os slots
OpenMPI: identifique esses casos como sobrealocação, não como CPUs físicas
adicionais. O exemplo desativa binding MPI e fixação OpenMP.

Registre a máquina junto ao CSV, antes da coleta:

```bash
{
  date -Iseconds
  nproc
  lscpu
  free -h
  g++ --version
  mpirun --version
} > dados/nova_coleta/maquina.txt
```

Acrescente flags, variáveis do comando, afinidade, limites efetivos de CPUs e
eventual sobrealocação. Compare versões da mesma máquina e rodada.

O analisador gera `resumo.csv`, três `tabela_forte_n*.csv` e `tabela_fraca.csv`.
O resumo distingue `S_seq=T_seq/T_p`, `S_1=T_1/T_p` da própria versão e `E=S/p`.
A eficiência fraca é `T_versão(12,5M,1)/T_versão(12,5M*p,p)`. O gerador exporta
seis figuras de tempo, speedup e eficiência sem modificar as tabelas. Consulte
as figuras históricas em `graficos/` e a
[análise experimental](secoes/analise_experimental.md).

O tempo é a janela interna do [protocolo](secoes/protocolo_medicao.md). Inclui
processamento, jump-ahead e redução; OpenMP inclui criação das threads. MPI
exclui inicialização/finalização, distribuição e barreira iniciais e a redução
usada para comunicar o tempo. Não equivale ao tempo externo de `mpirun`.

Os scripts `scripts/medir_baseline.sh`, `scripts/medir_perfilamento.sh` e
`scripts/amdahl.cpp` continuam disponíveis. Execute os dois primeiros com `bash`
na raiz de uma cópia separada: eles substituem os CSVs históricos. Compile a
previsão com `g++ -O2 -std=c++17 -o scripts/amdahl scripts/amdahl.cpp`.

## Situação e limitações

O PR #14 já incorpora os commits dos PRs #15 e #16; essa relação não transfere
a autoria das implementações ao autor do #14. As correções desta integração
estão em branch própria, antes de publicação ou merge na main.

A análise separa os dados do Gui, os da frente MPI da Dani e a coleta local de
integração. Nenhum speedup usa tempo sequencial de outra máquina. O fator 2 do
MPI nos dados do Gui permanece uma observação daquele ambiente, sem causa
comprovada. A investigação está descrita na análise experimental.

Faltam medições e demonstração ao vivo no laboratório, com CPU, versões,
binding e recursos efetivos registrados. WSL não garante os mesmos tempos lá.
A revisão estrutural e a repetibilidade sustentam a corretude do OpenMP, mas a
tentativa anterior com ThreadSanitizer/GCC-libgomp foi inconclusiva: o alerta da
redução também ocorreu em um controle mínimo correto. Não foi contado como
aprovação dinâmica de ausência de corridas.

Os testes concluídos e o parecer de integração estão em
[validacao_integracao.md](secoes/validacao_integracao.md).
