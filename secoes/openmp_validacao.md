# Geração aleatória e validação no OpenMP

## Estado do gerador

O baseline usa um único estado `s` no gerador `xorshift`. Esse estado não será compartilhado entre threads. Cada thread manterá uma cópia privada e processará um intervalo contíguo das iterações originais.

Usar simplesmente `semente_base + tid` produziria execuções repetíveis, mas alteraria a sequência e poderia mudar `dentro`. Como o enunciado exige exatamente o mesmo resultado do baseline, essa alternativa não será aceita como solução final.

## Preservação da sequência original

O estado inicial de cada thread deverá ser aquele que o baseline teria no início do seu intervalo. Como cada ponto consome duas chamadas de `xorshift`, uma thread cujo bloco começa em `inicio` deverá iniciar no estado correspondente a `2 * inicio` transições do gerador.

Esse posicionamento será obtido por uma técnica determinística de *skip-ahead* ou *jump-ahead*. Assim, as threads processarão trechos diferentes da mesma sequência original, sem repetição ou omissão de pontos e sem compartilhar estado mutável.

## Critério de corretude

Para cada entrada, a versão OpenMP deverá produzir exatamente os mesmos valores de `dentro` e `pi` do baseline, tanto com 1 thread quanto com 2, 4 e 8 threads. Uma estimativa apenas próxima de π não satisfará esse critério.

Também será verificado se a soma dos tamanhos dos blocos é igual a `n`, se os intervalos são disjuntos e se execuções repetidas produzem o mesmo resultado.

## Protocolo futuro de desempenho

Para cada tamanho de entrada e quantidade de threads, será descartada uma execução de aquecimento e serão realizadas três execuções válidas. A mediana dos tempos será utilizada para calcular:

```text
S(p) = T(1) / T(p)
E(p) = S(p) / p
```

Serão discutidos o overhead de criação e sincronização das threads, o custo da redução, o posicionamento do gerador e a saturação ao ultrapassar o número de núcleos físicos disponíveis.
