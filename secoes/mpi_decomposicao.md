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

```

Essa estratégia garante que todos os `n` pontos sejam processados e que a diferença de carga entre dois processos seja de, no máximo, um ponto.

## Contagem local

Cada processo executará a simulação apenas para os seus `n_local` pontos e manterá sua própria variável `dentro_local`. Dessa forma, não haverá atualização simultânea de uma mesma variável, pois cada processo possui memória independente.

Ao final do processamento, as contagens locais deverão ser combinadas para formar a quantidade global de pontos dentro do círculo. Essa combinação será realizada por uma operação coletiva de redução, detalhada no planejamento de comunicação MPI.

## Dados compartilhados entre os processos

Todos os processos precisam conhecer:

- o número total de pontos `n`;
- a quantidade total de processos;
- o identificador individual de cada processo;
- a estratégia utilizada para gerar os números aleatórios.

O valor de `n` poderá ser lido pelo processo raiz e distribuído aos demais processos com `MPI_Bcast`. Cada processo obterá seu identificador e a quantidade total de processos por meio de `MPI_Comm_rank` e `MPI_Comm_size`.

## Responsabilidade do processo raiz

O processo de `rank 0` será responsável por:

- receber ou interpretar o valor de entrada;
- distribuir os dados necessários;
- participar da simulação;
- receber a contagem global;
- calcular a estimativa final por meio de `4.0 * dentro_global / n`;
- apresentar o valor estimado de π e o tempo de execução.

Os demais processos realizarão sua parcela da simulação e enviarão suas contagens locais por meio da operação coletiva.

## Comunicação e escalabilidade

O algoritmo apresenta baixo volume de comunicação, pois os processos trabalham de forma independente durante quase toda a simulação. A comunicação é necessária principalmente no início, para disponibilizar o valor de `n`, e no final, para combinar as contagens locais.

Como o custo computacional cresce com a quantidade de pontos, enquanto a quantidade de dados comunicados permanece pequena, o problema apresenta potencial para paralelização com MPI. Entretanto, o desempenho real dependerá do número de processos, dos recursos disponíveis e dos custos de inicialização, sincronização e comunicação.