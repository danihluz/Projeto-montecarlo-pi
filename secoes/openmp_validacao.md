# Geração Aleatória e Validação

## Independência do Estado Gerador
O baseline utiliza a função `xorshift` dependente de uma variável de estado `s` compartilhada. No OpenMP, compartilhar esse estado geraria condições de corrida. Para garantir a independência, cada thread precisará de um estado e de uma semente própria.

## Reprodutibilidade e Validação
O enunciado exige validação contra o baseline, porém sementes diferentes por thread produzirão uma sequência diferente da versão puramente sequencial, o que pode alterar o valor exato da variável `dentro`. Para garantir a reprodutibilidade, a estratégia adotará um modelo determinístico para a geração das sementes locais (ex: baseadas no ID da thread). Isso assegura que execuções repetidas com o mesmo número de threads gerem resultados consistentes, mesmo que ligeiramente divergentes do *baseline* de 1 thread.

## Plano de Testes Futuro
Para a avaliação de tempo, *speedup* e eficiência, serão realizados testes com 1, 2, 4 e 8 threads. O tempo será aferido após descartar o primeiro aquecimento de cache e extraindo a mediana de três medições válidas. Serão medidos os impactos de criação das threads e o comportamento ao atingir o limite de núcleos físicos da máquina.