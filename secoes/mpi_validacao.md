# Comunicação, redução e validação da versão MPI

## Inicialização do ambiente MPI

A futura versão paralela deverá iniciar o ambiente de execução com `MPI_Init`. Em seguida, cada processo obterá seu identificador por meio de `MPI_Comm_rank` e a quantidade total de processos com `MPI_Comm_size`.

O identificador `rank` permitirá determinar a parcela da simulação executada por cada processo. O processo de `rank 0` será utilizado como raiz e ficará responsável pela entrada, pelo cálculo final de π e pela apresentação dos resultados.

Ao final da execução, todos os processos deverão encerrar corretamente o ambiente por meio de `MPI_Finalize`.

## Distribuição da entrada

O processo raiz deverá ler o número total de pontos `n`. Em seguida, o valor será enviado aos demais processos com:

```cpp
MPI_Bcast(&n, 1, MPI_LONG, 0, MPI_COMM_WORLD);