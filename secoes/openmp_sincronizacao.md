# Sincronização e Condição de Corrida

## O Problema na Variável Compartilhada
O laço possui uma variável crítica compartilhada: `dentro`, que contabiliza os pontos na área do círculo. Se múltiplas threads tentarem incrementar essa variável simultaneamente, ocorrerá uma condição de corrida (*race condition*), resultando em atualizações simultâneas perdidas e um valor final incorreto.

## Avaliação de Alternativas
Três abordagens de sincronização foram analisadas:
* **`critical`**: Garantiria a exclusão mútua, mas forçaria a serialização do incremento em cada iteração, degradando o desempenho.
* **`atomic`**: Utiliza instruções atômicas de hardware, mas ainda causaria contenção no barramento de memória devido à alta frequência de atualizações.
* **`reduction(+:dentro)`**: É a escolha justificada e mais apropriada. O OpenMP criará cópias privadas da variável `dentro` para cada thread, permitindo incrementos locais independentes. Ao final do laço, os valores privados serão combinados na variável global com eficiência máxima.