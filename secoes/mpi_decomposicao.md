# Decomposição do trabalho com MPI

## Região paralelizável

No programa sequencial, a maior parte do processamento ocorre no laço que percorre os `n` pontos da simulação de Monte Carlo. Em cada iteração, o programa gera as coordenadas aleatórias `x` e `y`, verifica se o ponto satisfaz a condição `x*x + y*y <= 1.0` e, quando isso acontece, incrementa a variável `dentro`.

Como a verificação de cada ponto pode ser realizada de forma independente, esse laço constitui a principal região a ser distribuída entre processos MPI. As etapas de leitura da entrada, cálculo final de π e apresentação do resultado exigem pouco processamento e podem permanecer sob responsabilidade do processo raiz.

## Divisão dos pontos entre os processos

Considerando `p` processos, cada processo receberá inicialmente:

`n / p`

pontos para processar. Quando `n` não for divisível exatamente por `p`, os pontos restantes serão distribuídos entre os primeiros processos. A quantidade local de pontos do processo de identificador `rank` poderá ser calculada por:

```text
base = n / p
resto = n % p
n_local = base + (rank < resto ? 1 : 0)