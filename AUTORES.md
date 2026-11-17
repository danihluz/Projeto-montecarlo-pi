# Autores e responsabilidades

## Código de referência

`baseline/02_montecarlo_pi.cpp` foi fornecido pelo professor Rodrigo Gonçalves
Pinto. Seu algoritmo e conteúdo foram preservados; o baseline não é uma
implementação original de um integrante do grupo.

## Guilherme Ferreira de Souza

Análise do baseline, cópia instrumentada para perfilamento, identificação do
hotspot, Lei de Amdahl, protocolo experimental, gabarito, scripts originais de
coleta/análise, medições consolidadas e gráficos históricos.

Branches: `baseline-perfilamento` (Marco 1) e `marco2-medicao` (Marco 2).
PR do Marco 2: [#14](https://github.com/danihluz/Projeto-montecarlo-pi/pull/14).

## Danielly de Sousa Luz

Implementação MPI, decomposição entre processos, jump-ahead MPI, broadcast,
reduções, validação e medições da frente MPI. Organização da documentação e
integração das contribuições.

Branches: `plano-mpi-documentacao` (Marco 1), `mpi-dani` (Marco 2) e
`integracao-marco2` (correções de integração).
PR da implementação MPI: [#15](https://github.com/danihluz/Projeto-montecarlo-pi/pull/15).

Na branch de integração, as correções no coletor originalmente escrito por
Guilherme, o Makefile comum, a documentação, as regressões do coletor e o gerador
reproduzível de gráficos foram preparados sob responsabilidade de Danielly,
com apoio de IA. Essas revisões não transferem a autoria do código original do
Gui nem das implementações OpenMP/MPI.

## Heitor dos Santos Ribeiro

Implementação OpenMP, distribuição estática em blocos, redução da contagem,
estado privado e jump-ahead por thread, testes de corretude/repetibilidade e
documentação da frente OpenMP.

Branches: `plano-openmp` (Marco 1) e `openmp-heitor` (Marco 2).
PR do Marco 2: [#16](https://github.com/danihluz/Projeto-montecarlo-pi/pull/16).

## Histórico e trabalho do trio

O PR #14 já contém merges dos commits dos PRs #16 e #15. Os commits dos três
integrantes foram preservados na integração; a presença de um arquivo em um PR
não significa autoria exclusiva de quem abriu esse PR. Os fontes dos três
algoritmos não foram modificados pelas correções de integração.

Cada integrante deve compreender também as demais frentes para a arguição
cruzada. A coleta e a demonstração finais no laboratório são uma pendência do trio.
