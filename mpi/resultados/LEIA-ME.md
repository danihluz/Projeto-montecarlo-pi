# Registro de validação e medições MPI

Coleta iniciada em 12/11/2026 às 22:55, horário de São Paulo. Ambiente:
Ubuntu 26.04.1 no WSL2, GCC 15.2, MPICH 4.3.2 extraído localmente, oito CPUs
lógicas disponíveis. Caracterização completa em `maquina.txt`.

## Corretude

- 2.335 comparações de estados do jump-ahead com a função xorshift original
  do professor: todas iguais, com cinco sementes e deslocamentos até
  300.000.000 transições, incluindo limites e vizinhanças dos blocos.
- 119 partições verificadas: cobertura de `n`, continuidade dos intervalos e
  diferença de carga de no máximo um ponto. Há casos com mais processos que
  pontos.
- 155.120 coordenadas verificadas individualmente contra o gerador original
  nas entradas pequenas: todas iguais.
- 108 comparações dos executáveis completos, com 1, 2, 3, 4, 6 e 8 processos:
  `dentro` e `pi` exatamente iguais ao baseline. Abrangem 11 entradas de teste
  e os sete tamanhos do gabarito do PR #14. `comparacoes.csv` contém cada caso.
- Uma única linha no formato exato foi exigida em todas as execuções válidas,
  com stderr vazio. O teste Hydra com identificação de rank produziu:

```text
[0] n=17  pi=3.058824  dentro=13  tempo=0.001685 s
```

- A execução sem argumento preservou o padrão de 50 milhões e coincidiu com
  o baseline. Zero e `-1` foram rejeitados com retorno 1 e uma mensagem da
  raiz em stderr; são falhas esperadas de entrada, não divergências.
- As cópias intactas do coletor e analisador do Gui concluíram com retorno
  zero: 99 medições válidas, todas `OK`, além dos 33 aquecimentos descartados.
  O protocolo executou três repetições por configuração. Os arquivos usados
  e seus hashes estão em `origens_pr14.json`, fixados no commit
  `e0917954201eeb854f094f36b9f94f41a3dd81a1`.

Não ocorreu divergência ou falha nas execuções válidas desta bateria.
`validacao.log` registra os comandos, saídas e retornos; `validacao.json`
resume as verificações. O baseline foi compilado para uma pasta temporária
em `mpi/`, preservando o executável preexistente em `baseline/`.

## Exemplo de escalabilidade forte: 100 milhões de pontos

Em todas as execuções: `pi=3.141499`, `dentro=78537472`. A mediana sequencial
medida nesta mesma coleta foi **0,444217 s**.

| Processos MPI | Mediana (s) | Speedup contra sequencial |
|---:|---:|---:|
| 1 | 0,440239 | 1,009036 |
| 2 | 0,238019 | 1,866309 |
| 4 | 0,136204 | 3,261409 |
| 6 | 0,104307 | 4,258746 |
| 8 | 0,075016 | 5,921630 |
| 12, sobrealocado | 0,091994 | 4,828761 |

O coletor fixa 12 processos como parte de seu protocolo; mantivemos seu
conteúdo inalterado. Como há apenas oito CPUs lógicas disponíveis, os tempos
com 12 processos incluem disputa adicional por CPU. Essa configuração não
comprova escalabilidade em uma máquina com 12 CPUs disponíveis.

Os números são medianas de três execuções, precedidas de um aquecimento. O
tempo é interno à região definida no protocolo, incluindo jump-ahead e a
redução das contagens; exclui inicialização/finalização MPI e a redução usada
para comunicar os próprios tempos. Não é o tempo total do comando externo.

`medicoes.csv` contém as 99 medições originais. `resumo.csv` contém as medianas,
speedups contra o sequencial e contra um worker da própria versão, eficiências
e eficiência fraca. `tabela_forte_n*.csv` e `tabela_fraca.csv` são as saídas
originais do analisador do Gui. As colunas OpenMP permanecem vazias porque
essa implementação não fez parte dos testes.

## Limites e próximos passos

Estes resultados são locais; ainda devem ser repetidos no laboratório, com
caracterização do ambiente. A versão OpenMP precisa ser integrada e medida
pelo grupo. O PR #14 permanece separado: não houve merge, push ou abertura
de PR nesta tarefa. Nenhum arquivo fora de `mpi/` foi alterado.

O PDF original do enunciado não estava disponível para conferência. Foram
seguidos o baseline do professor, os requisitos fornecidos pela Danielly e o
contrato do PR #14 inspecionado.
