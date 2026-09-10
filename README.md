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
- `secoes/`: análises técnicas e planos de paralelização com OpenMP e MPI;
- `relatorio/`: relatório do Marco 1 em PDF;
- `AUTORES.md`: divisão das responsabilidades do grupo.

## Ambiente utilizado

O projeto utiliza o ambiente Linux disponibilizado pela disciplina por meio de Docker e Visual Studio Code Dev Containers.

### Requisitos

- compilador `g++`;
- otimização `-O2`;
- OpenMP;
- OpenMPI.

## Compilação do baseline

Na pasta principal do projeto, execute:

```bash
g++ -O2 -o baseline/02_montecarlo_pi baseline/02_montecarlo_pi.cpp
```

## Execução do baseline

```bash
./baseline/02_montecarlo_pi 50000000
```

O valor informado ao programa representa a quantidade de pontos utilizada na estimativa de Pi.

## Metodologia de medição

Para cada tamanho de entrada:

1. realizar uma execução de aquecimento e descartá-la;
2. realizar três execuções válidas;
3. registrar o resultado e o tempo de cada execução;
4. calcular a mediana dos três tempos válidos.

Serão utilizados pelo menos três tamanhos de entrada. Os tempos registrados no projeto devem resultar de execuções reais no ambiente da disciplina.

## Organização do trabalho

O desenvolvimento foi dividido em três frentes:

- análise do baseline, perfilamento e aplicação da Lei de Amdahl;
- planejamento da paralelização com OpenMP;
- planejamento da paralelização com MPI e organização da documentação.

Cada integrante trabalha em uma branch própria. Após a conclusão, as alterações são enviadas para revisão por meio de Pull Requests antes da incorporação à branch `main`.

## Situação do projeto

O Marco 1 contempla:

- análise do algoritmo sequencial;
- medições do baseline;
- perfilamento e identificação do hotspot;
- estimativa de speedup pela Lei de Amdahl;
- planejamento da versão OpenMP;
- planejamento da versão MPI;
- documentação da metodologia e da divisão das responsabilidades.