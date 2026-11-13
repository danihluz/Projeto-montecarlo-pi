/* OpenMP — Estimativa de pi por Monte Carlo
 * Heitor dos Santos Ribeiro — IESB 2026/2, CCO085
 * Preserva a sequencia e a saida de baseline/02_montecarlo_pi.cpp.
 * Compilar: g++ -O2 -fopenmp -o openmp/02_montecarlo_pi_omp openmp/02_montecarlo_pi_openmp.cpp
 * Executar: OMP_NUM_THREADS=4 ./openmp/02_montecarlo_pi_omp 50000000
 */
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <ctime>
#include <omp.h>
#include "xorshift_jump.h"

static double agora() {
    timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

int main(int argc, char** argv) {
    long n = (argc > 1) ? atol(argv[1]) : 50000000L;
    long dentro = 0;

    double t0 = agora();
    const uint64_t semente = 88172645463325252ULL;
    if (n > 0) {
        // Conversao ANTES de multiplicar: 2*(n-1) cabe em uint64_t no Linux
        // com long de 64 bits, mesmo quando nao cabe no long com sinal.
        const montecarlo::JumpAhead salto(2ULL * static_cast<uint64_t>(n - 1));
        #pragma omp parallel default(none) shared(n, semente, salto) reduction(+:dentro)
        {
            const montecarlo::Bloco bloco = montecarlo::bloco_contiguo(
                n, omp_get_thread_num(), omp_get_num_threads());
            if (bloco.inicio < bloco.fim) {
                uint64_t s = salto.avancar(semente, 2ULL * static_cast<uint64_t>(bloco.inicio));
                for (long i = bloco.inicio; i < bloco.fim; ++i) {
                    double x = (montecarlo::xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
                    double y = (montecarlo::xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
                    if (x*x + y*y <= 1.0) dentro++;
                }
            }
        }
    }
    double pi = 4.0 * (double)dentro / (double)n;
    double t1 = agora();

    printf("n=%ld  pi=%.6f  dentro=%ld  tempo=%.6f s\n", n, pi, dentro, t1 - t0);
    return 0;
}
