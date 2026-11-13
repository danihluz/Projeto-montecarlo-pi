#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <omp.h>
#include "xorshift_jump.h"

static void exigir(bool condicao, const char* mensagem) {
    if (!condicao) {
        std::fprintf(stderr, "FALHOU: %s\n", mensagem);
        std::exit(1);
    }
}

// Referencia iterativa independente da implementacao do salto.
static uint64_t passo(uint64_t s) {
    s ^= s << 13;
    s ^= s >> 7;
    s ^= s << 17;
    return s;
}

int main(int argc, char** argv) {
    if (argc == 2 && std::strcmp(argv[1], "--equipe") == 0) {
        int participantes = 0;
        #pragma omp parallel reduction(+:participantes)
        { participantes += 1; }
        std::printf("threads=%d\n", participantes);
        return 0;
    }
    const montecarlo::JumpAhead salto(UINT64_MAX);
    const uint64_t sementes[] = {0, 1, 88172645463325252ULL, UINT64_MAX, 1ULL << 63};
    for (uint64_t semente : sementes) {
        uint64_t referencia = semente;
        for (uint64_t k = 0; k <= 10000; ++k) {
            exigir(salto.avancar(semente, k) == referencia, "salto != avanco iterativo");
            referencia = passo(referencia);
        }
        const uint64_t deslocamentos[] = {1ULL << 31, 1ULL << 32, 1ULL << 62,
                                         1ULL << 63, UINT64_MAX - 1};
        for (uint64_t k : deslocamentos) {
            exigir(salto.avancar(semente, k + 1) == passo(salto.avancar(semente, k)),
                   "transicao apos salto de indice grande");
        }
        exigir(salto.avancar(salto.avancar(semente, 1ULL << 63), (1ULL << 63) - 1)
                   == salto.avancar(semente, UINT64_MAX), "composicao ate UINT64_MAX");
    }
    for (unsigned bit = 0; bit < 64; ++bit) {
        exigir(salto.avancar(1ULL << bit, 1) == passo(1ULL << bit), "vetor da base");
    }
    const montecarlo::JumpAhead identidade(0);
    exigir(identidade.avancar(88172645463325252ULL, 0) == 88172645463325252ULL,
           "salto de zero passos");

    for (long n = 0; n <= 257; ++n) {
        for (int p = 1; p <= 32; ++p) {
            long anterior = 0;
            for (int tid = 0; tid < p; ++tid) {
                const auto bloco = montecarlo::bloco_contiguo(n, tid, p);
                exigir(bloco.inicio == anterior, "lacuna ou sobreposicao");
                exigir(bloco.fim >= bloco.inicio && bloco.fim <= n, "limites do bloco");
                anterior = bloco.fim;
            }
            exigir(anterior == n, "cobertura incompleta");
        }
    }
    const long grandes[] = {LONG_MAX / 2, LONG_MAX - 1, LONG_MAX};
    for (long n : grandes) {
        for (int p = 1; p <= 32; ++p) {
            long anterior = 0;
            for (int tid = 0; tid < p; ++tid) {
                const auto bloco = montecarlo::bloco_contiguo(n, tid, p);
                exigir(bloco.inicio == anterior && bloco.fim >= bloco.inicio
                           && bloco.fim <= n, "particionamento perto de LONG_MAX");
                anterior = bloco.fim;
            }
            exigir(anterior == n, "cobertura perto de LONG_MAX");
        }
    }
    std::puts("OK: salto iterativo, vetores da base, indices de 64 bits e cobertura dos blocos.");
}
