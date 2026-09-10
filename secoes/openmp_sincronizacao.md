# Sincronização e condição de corrida no OpenMP

## Condição de corrida

Se várias threads executarem `dentro++` sobre a mesma variável sem proteção, duas ou mais poderão ler o mesmo valor e sobrescrever atualizações umas das outras. Isso caracteriza uma condição de corrida e produz uma contagem incorreta.

O estado `s` do gerador `xorshift` também não pode ser compartilhado: cada chamada altera esse estado, de modo que acessos simultâneos corromperiam a sequência e tornariam o resultado não determinístico.

## Alternativas de sincronização

- `critical`: garante exclusão mútua, mas serializa os incrementos e tende a introduzir grande overhead.
- `atomic`: é mais leve que `critical`, porém ainda cria contenção sobre uma variável atualizada milhões de vezes.
- `reduction(+:dentro)`: fornece uma cópia privada do contador para cada thread e combina os valores ao final, evitando contenção a cada iteração.

Por isso será utilizada uma redução por soma. `n` e a semente-base serão compartilhados apenas para leitura; o identificador da thread, os limites do bloco, o estado do gerador, `x` e `y` serão privados; `dentro` participará da redução.

Essa escolha preserva a corretude da contagem e reduz o custo de sincronização em comparação com `critical` e `atomic`.
