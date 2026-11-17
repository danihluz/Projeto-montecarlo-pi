// Compara com a funcao xorshift do proprio baseline, sem altera-lo.
#define main main_baseline_nao_executado
#include "../baseline/02_montecarlo_pi.cpp"
#undef main

#include <algorithm>
#include <set>
#include <vector>
#include "montecarlo.hpp"

static void exigir(bool condicao, const char* mensagem) {
    if (!condicao) {
        fprintf(stderr, "FALHA: %s\n", mensagem);
        std::exit(1);
    }
}

int main() {
    const std::vector<long> entradas = {
        1, 2, 3, 5, 7, 10, 17, 31, 1001, 10003,
        10000000, 12500000, 25000000, 50000000,
        75000000, 100000000, 150000000
    };
    const std::vector<int> workers = {1, 2, 3, 4, 6, 8, 12};
    std::set<uint64_t> posicoes = {
        0, 1, 2, 3, 4, 7, 8, 9, 31, 32, 33, 63, 64, 65,
        127, 128, 129, 255, 256, 257, 1023, 1024, 1025,
        65535, 65536, 65537, 999999, 1000000, 1000001,
        16777215, 16777216, 16777217, 134217727, 134217728,
        134217729, 299999999, 300000000
    };

    size_t particoes = 0;
    size_t coordenadas = 0;
    for (long n : entradas) {
        for (int p : workers) {
            long fim_anterior = 0, menor = n, maior = 0;
            uint64_t referencia = montecarlo::semente;
            for (int rank = 0; rank < p; ++rank) {
                const auto bloco = montecarlo::dividir(n, rank, p);
                exigir(bloco.inicio == fim_anterior, "lacuna ou sobreposicao nos blocos");
                exigir(bloco.quantidade >= 0, "bloco negativo");
                fim_anterior += bloco.quantidade;
                menor = std::min(menor, bloco.quantidade);
                maior = std::max(maior, bloco.quantidade);

                // Inicio, fim e vizinhanca de cada limite, em transicoes.
                for (long ponto : {bloco.inicio, fim_anterior}) {
                    const uint64_t limite = uint64_t{2} * static_cast<uint64_t>(ponto);
                    posicoes.insert(limite);
                    if (limite > 0) posicoes.insert(limite - 1);
                    if (limite < 300000000) posicoes.insert(limite + 1);
                }

                if (n <= 10003) {
                    uint64_t local = montecarlo::avancar(montecarlo::semente,
                        uint64_t{2} * static_cast<uint64_t>(bloco.inicio));
                    exigir(local == referencia, "estado inicial do bloco");
                    for (long i = 0; i < bloco.quantidade; ++i) {
                        for (int coordenada = 0; coordenada < 2; ++coordenada) {
                            exigir(montecarlo::xorshift(local) == xorshift(referencia),
                                   "coordenada diferente do baseline");
                            ++coordenadas;
                        }
                    }
                }
            }
            exigir(fim_anterior == n, "soma dos blocos diferente de n");
            exigir(maior - menor <= 1, "carga desequilibrada");
            ++particoes;
        }
    }

    // Um percurso sequencial por semente ate a maior posicao (300 milhoes).
    const uint64_t sementes[] = {montecarlo::semente, 0, 1,
                                 UINT64_MAX, uint64_t{1} << 63};
    size_t estados = 0;
    for (uint64_t semente : sementes) {
        uint64_t referencia = semente, anterior = 0;
        for (uint64_t posicao : posicoes) {
            for (uint64_t i = anterior; i < posicao; ++i) xorshift(referencia);
            exigir(montecarlo::avancar(semente, posicao) == referencia,
                   "jump-ahead diferente do xorshift sequencial original");
            anterior = posicao;
            ++estados;
        }
    }
    printf("OK: %zu estados, 5 sementes, deslocamentos ate 300000000; "
           "%zu particoes; %zu coordenadas identicas ao baseline.\n",
           estados, particoes, coordenadas);
    return 0;
}
