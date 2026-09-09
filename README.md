# Estimativa de Pi por Monte Carlo

Projeto acadêmico desenvolvido para a disciplina de Programação Paralela (CCO085), do curso de Ciência da Computação do IESB, no segundo semestre de 2026.

## Objetivo

Analisar o programa sequencial que estima o valor de Pi pelo método de Monte Carlo e planejar sua paralelização utilizando OpenMP e MPI.

## Integrantes

- Guilherme Ferreira de Souza
- Danielly de Sousa Luz
- Heitor dos Santos Ribeiro

A responsabilidade de cada integrante está descrita no arquivo `AUTORES.md`.

## Estrutura do projeto

- `baseline/`: código sequencial fornecido pelo professor;
- `dados/`: resultados das medições em formato CSV;
- `scripts/`: scripts utilizados para executar as medições;
- `relatorio/`: relatório do Marco 1 em PDF;
- `AUTORES.md`: divisão das responsabilidades do grupo.

## Ambiente utilizado

O projeto utiliza o ambiente Linux disponibilizado pela disciplina por meio de Docker e Visual Studio Code Dev Containers.

Requisitos:

- compilador G++;
- otimização `-O2`;
- OpenMP;
- OpenMPI.

## Compilação do baseline

Na pasta principal do projeto, execute:

```bash
g++ -O2 -o baseline/02_montecarlo_pi baseline/02_montecarlo_pi.cpp

```

## Execução

```bash
./baseline/02_montecarlo_pi 50000000
```

O valor informado ao programa representa a quantidade de pontos utilizada na estimativa.

## Metodologia de medição

Para cada tamanho de entrada:

1. realizar uma execução de aquecimento e descartá-la;
2. realizar três execuções válidas;
3. registrar o resultado e o tempo de cada execução;
4. utilizar a mediana dos três tempos.

Serão utilizados pelo menos três tamanhos de entrada.

## Situação do projeto

O Marco 1 contempla a análise do baseline, o perfilamento, a estimativa pela Lei de Amdahl e o planejamento das versões OpenMP e MPI.