1.  Ambiente. Anexar dados/maquina.txt (Ryzen 5 3600: 6 núcleos físicos, 12 lógicos; WSL2; g++ 13.3.0). Para as medições finais, repetir na máquina do laboratório e registrar em dados/maquina_lab.txt, incluindo mpirun --version.
2.  Compilação. Sequencial: g++ -O2. OpenMP: g++ -O2 -fopenmp. MPI: mpic++ -O2. Mesmo nível de otimização nas três.
3.  Entrada. argv[1] = número total de pontos n. O número de threads vem da variável de ambiente OMP_NUM_THREADS (o programa não deve fixá-lo no código); o de processos vem de mpirun -np p.
4.  Saída (contrato). Exatamente uma linha, no mesmo formato do baseline, impressa uma única vez (no MPI, só pelo rank 0): n=<n>  pi=<%.6f>  dentro=<d>  tempo=<%.6f> s.
5.  O que o tempo mede. Segundos entre o início da região paralela e o resultado final de π calculado. Inclui o posicionamento do gerador (jump-ahead), a criação das threads e a redução. No MPI, medir após MPI_Barrier, até depois do MPI_Reduce, usando o máximo entre os ranks; ficam de fora MPI_Init e MPI_Finalize. O baseline já mede o laço e o cálculo de π.
6.  Repetições. Por configuração: 1 execução de aquecimento (descartada) e 3 válidas; vale a mediana. É o mesmo protocolo do Marco 1.
7.  Workers (threads ou processos). 1, 2, 4, 6, 8 e 12.
8.  Escalabilidade forte. n fixo em 10.000.000, 50.000.000 e 100.000.000; varia-se o número de workers.
9.  Escalabilidade fraca. n = 12.500.000 × p (12,5M, 25M, 50M, 75M, 100M e 150M para p = 1, 2, 4, 6, 8, 12).
10.  Corretude. dentro e pi devem ser idênticos ao gabarito do baseline (dados/gabarito.csv) para o mesmo n, com qualquer número de workers. Proximidade numérica não vale (PDF, Seção 1 e 5.2).
11.  Métricas. S_seq(p) = T_seq(n) / T_p(n); S_1(p) = T_1(n) / T_p(n) (mesma versão com 1 worker); E(p) = S(p) / p; eficiência fraca = T_1(12,5M) / T_p(12,5M × p).
12.  Reprodutibilidade. Os comandos exatos são os de scripts/gerar_gabarito.sh e scripts/coletar.sh.