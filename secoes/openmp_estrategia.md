# Estratégia de Paralelização com OpenMP

## Identificação da Região Paralelizável
A principal região paralelizável do código de referência é o laço `for (long i = 0; i < n; i++)`, responsável pelo sorteio dos pontos e cálculo da equação da circunferência. Esta estrutura apresenta um paralelismo quase perfeito, pois cada iteração do laço é independente. As operações que precedem o laço (leitura de parâmetros e marcação do tempo inicial) e as que o sucedem (cálculo final de pi e impressão dos resultados) permanecerão sequenciais.

## Divisão do Trabalho e Escalonamento
Para distribuir as iterações, será utilizada a diretiva `#pragma omp parallel for`. A execução será avaliada com 1, 2, 4 e 8 threads. Como o processamento possui custo computacional homogêneo (apenas chamadas à função aleatória e operações aritméticas simples), a política de escalonamento mais adequada é o `schedule(static)`. Neste modelo, as iterações são divididas em blocos iguais estaticamente. Políticas como `dynamic` ou `guided` seriam contraproducentes, pois adicionariam *overhead* sem benefícios significativos dada a ausência de desbalanceamento natural.