// Marco 2 - MPI - Danielly de Sousa Luz.
// Compilar e executar: consulte mpi/README.md.
#include <mpi.h>
#include <cstdio>
#include <cstdlib>
#include "montecarlo.hpp"

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    int rank, processos;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &processos);

    long n = 0;
    if (rank == 0) n = (argc > 1) ? atol(argv[1]) : 50000000L;
    MPI_Bcast(&n, 1, MPI_LONG, 0, MPI_COMM_WORLD);
    if (n <= 0) {
        if (rank == 0) fprintf(stderr, "ERRO: n deve ser positivo.\n");
        MPI_Finalize();
        return 1;
    }

    MPI_Barrier(MPI_COMM_WORLD);
    const double t0 = MPI_Wtime();

    const montecarlo::Bloco bloco = montecarlo::dividir(n, rank, processos);
    // Converter antes de multiplicar evita overflow de long em 2 * inicio.
    uint64_t s = montecarlo::avancar(montecarlo::semente,
                                    uint64_t{2} * static_cast<uint64_t>(bloco.inicio));
    long dentro_local = 0;
    for (long i = 0; i < bloco.quantidade; ++i) {
        double x = (montecarlo::xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
        double y = (montecarlo::xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
        if (x*x + y*y <= 1.0) dentro_local++;
    }

    long dentro_global = 0;
    MPI_Reduce(&dentro_local, &dentro_global, 1, MPI_LONG, MPI_SUM,
               0, MPI_COMM_WORLD);
    double pi = 0.0;
    if (rank == 0) pi = 4.0 * (double)dentro_global / (double)n;

    // Inclui posicionamento, simulacao, reducao das contagens e calculo de pi.
    const double tempo_local = MPI_Wtime() - t0;
    double tempo = 0.0;
    MPI_Reduce(&tempo_local, &tempo, 1, MPI_DOUBLE, MPI_MAX,
               0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("n=%ld  pi=%.6f  dentro=%ld  tempo=%.6f s\n",
               n, pi, dentro_global, tempo);
    }
    MPI_Finalize();
    return 0;
}
