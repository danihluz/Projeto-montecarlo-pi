# Estratégia de paralelização com OpenMP

## Região paralelizável

A principal região paralelizável é o laço `for (long i = 0; i < n; i++)`, no qual são gerados os pontos `(x, y)`, aplicado o teste `x*x + y*y <= 1.0` e atualizada a contagem `dentro`. Cada ponto pode ser testado de forma independente; por isso, o custo de `O(n)` pode ser distribuído entre threads.

A leitura de `n`, a inicialização do ambiente, o cálculo final de π e a impressão permanecerão sequenciais. A combinação das contagens ocorrerá ao final da região paralela.

## Divisão do trabalho

O plano utilizará uma região OpenMP com divisão estática de intervalos contíguos. Para `p` threads, cada uma receberá aproximadamente `n/p` pontos; o resto será distribuído entre as primeiras threads. Essa divisão permite associar a cada thread uma posição inicial exata da sequência do gerador, requisito necessário para reproduzir o baseline.

Em termos conceituais:

```cpp
#pragma omp parallel reduction(+:dentro)
{
    int tid = omp_get_thread_num();
    int p = omp_get_num_threads();
    long inicio = inicio_do_bloco(tid, p, n);
    long fim = fim_do_bloco(tid, p, n);
    uint64_t estado = estado_xorshift_na_posicao(2 * inicio);

    for (long i = inicio; i < fim; ++i) {
        double x = proximo_valor(estado);
        double y = proximo_valor(estado);
        if (x*x + y*y <= 1.0) dentro++;
    }
}
```

O pseudocódigo expressa o plano e não representa uma implementação já testada. A função de posicionamento do estado deverá ser implementada por uma técnica determinística de *skip-ahead* ou *jump-ahead*.

## Escalonamento

Como todas as iterações têm custo semelhante, a distribuição estática é a mais adequada. `dynamic` e `guided` acrescentariam decisões de escalonamento em tempo de execução sem vantagem relevante neste problema. Na implementação, a divisão manual contígua equivale ao objetivo de `schedule(static)` e facilita a inicialização correta de um gerador por thread.

A avaliação futura utilizará 1, 2, 4 e 8 threads, respeitando os recursos disponíveis na máquina.
