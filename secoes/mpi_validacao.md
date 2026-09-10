# Comunicação, redução e validação da versão MPI

## Inicialização do ambiente MPI

A futura versão paralela deverá iniciar o ambiente de execução com `MPI_Init`. Em seguida, cada processo obterá seu identificador por meio de `MPI_Comm_rank` e a quantidade total de processos com `MPI_Comm_size`.

O identificador `rank` permitirá determinar a parcela da simulação executada por cada processo. O processo de `rank 0` será utilizado como raiz e ficará responsável pela entrada, pelo cálculo final de π e pela apresentação dos resultados.

Ao final da execução, todos os processos deverão encerrar corretamente o ambiente por meio de `MPI_Finalize`.

## Distribuição da entrada

O processo raiz deverá ler o número total de pontos `n`. Em seguida, o valor será enviado aos demais processos com:

```cpp
MPI_Bcast(&n, 1, MPI_LONG, 0, MPI_COMM_WORLD);

```

Com o mesmo valor de `n` disponível em todos os processos, cada um poderá calcular sua quantidade local de pontos. Isso evita o envio individual de tarefas e reduz o volume de comunicação.

## Redução das contagens

Cada processo manterá uma variável privada `dentro_local`, que armazenará a quantidade de pontos de sua parcela localizada dentro do círculo.

Ao final do laço local, as contagens deverão ser somadas no processo raiz por meio de `MPI_Reduce`:

```cpp
MPI_Reduce(
    &dentro_local,
    &dentro_global,
    1,
    MPI_LONG,
    MPI_SUM,
    0,
    MPI_COMM_WORLD
);
```

A operação `MPI_SUM` é adequada porque o resultado global corresponde à soma das contagens produzidas por todos os processos. O uso de `MPI_Reduce` também evita a implementação manual de envios e recebimentos entre cada processo e a raiz.

Após a redução, somente o processo de `rank 0` deverá calcular:

```cpp
pi = 4.0 * (double)dentro_global / (double)n;
```

## Geração de números aleatórios

O baseline utiliza um gerador `xorshift` com uma semente fixa armazenada na variável `s`. Em MPI, cada processo possui memória independente e deverá possuir seu próprio estado do gerador.

Utilizar apenas sementes diferentes baseadas no `rank` evita o compartilhamento de estado, mas altera as sequências aleatórias e pode produzir uma contagem diferente do baseline. Portanto, essa solução não garante igualdade exata.

Para preservar o mesmo conjunto de pontos do programa sequencial, cada processo deverá receber um intervalo contíguo das iterações originais. O estado inicial do gerador de cada processo deverá corresponder ao estado que o baseline possuiria no início desse intervalo.

Como cada ponto consome duas chamadas de `xorshift`, o processo responsável por um intervalo iniciado no ponto `inicio_local` deverá começar no estado correspondente a `2 * inicio_local` avanços do gerador. Essa posição poderá ser obtida por uma técnica determinística de avanço do estado, conhecida como *skip-ahead* ou *jump-ahead*.

## Reprodutibilidade e corretude

A validação deverá verificar:

- se a soma de todos os valores de `n_local` é igual a `n`;
- se nenhum intervalo de pontos foi repetido ou ignorado;
- se `dentro_global` coincide com o valor `dentro` do baseline;
- se a estimativa de π é igual à produzida pelo programa sequencial;
- se o resultado se mantém em execuções repetidas;
- se o resultado permanece consistente com diferentes números de processos.

Caso sejam utilizadas sementes independentes sem equivalência com a sequência original, a comparação deverá considerar a proximidade estatística da estimativa de π, deixando explícito que não existe igualdade exata com o baseline.

## Protocolo de testes

A futura implementação deverá ser executada com 1, 2, 4 e 8 processos, desde que a máquina possua recursos suficientes. Para cada configuração, será realizada uma execução de aquecimento, seguida de três execuções válidas.

Deverão ser registrados:

- número total de pontos;
- número de processos;
- estimativa de π;
- quantidade global `dentro`;
- tempo de execução;
- mediana dos tempos;
- speedup;
- eficiência.

O speedup será calculado por:

```text
S(p) = T(1) / T(p)
```

A eficiência será calculada por:

```text
E(p) = S(p) / p
```

## Medição do tempo

O tempo da região paralela deverá ser medido com `MPI_Wtime`. Uma barreira poderá ser utilizada antes da medição para alinhar o início dos processos:

```cpp
MPI_Barrier(MPI_COMM_WORLD);
double inicio = MPI_Wtime();
```

Como a execução termina somente quando o processo mais lento conclui sua parcela, os tempos locais deverão ser combinados com `MPI_Reduce` e a operação `MPI_MAX`. O maior tempo representará o tempo efetivo da execução paralela.

## Overhead esperado

O desempenho real poderá ser afetado pela inicialização do MPI, distribuição dos dados, sincronização, redução das contagens, avanço determinístico do gerador e quantidade de núcleos disponíveis.

Para entradas pequenas, esses custos podem representar uma parcela significativa do tempo total. Para entradas maiores, espera-se que o custo da simulação predomine e permita melhor aproveitamento do paralelismo.