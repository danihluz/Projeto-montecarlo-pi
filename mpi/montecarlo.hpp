#ifndef MONTECARLO_MPI_HPP
#define MONTECARLO_MPI_HPP

#include <array>
#include <cstdint>

namespace montecarlo {

constexpr uint64_t semente = 88172645463325252ULL;

// Mesma transicao do baseline do professor.
inline uint64_t xorshift(uint64_t& s) {
    s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s;
}

// A coluna j e a imagem do bit j pela transformacao linear sobre GF(2).
using Transformacao = std::array<uint64_t, 64>;

inline uint64_t aplicar(const Transformacao& t, uint64_t estado) {
    uint64_t resultado = 0;
    for (unsigned j = 0; estado != 0; ++j, estado >>= 1) {
        if (estado & 1ULL) resultado ^= t[j];
    }
    return resultado;
}

// Retorna T^passos(estado), sem gerar os valores intermediarios.
inline uint64_t avancar(uint64_t estado, uint64_t passos) {
    if (passos == 0) return estado;

    Transformacao potencia;
    for (unsigned j = 0; j < 64; ++j) {
        uint64_t bit = uint64_t{1} << j;
        potencia[j] = xorshift(bit);
    }

    while (passos != 0) {
        if (passos & 1ULL) estado = aplicar(potencia, estado);
        passos >>= 1;
        if (passos == 0) break;

        Transformacao quadrado;
        for (unsigned j = 0; j < 64; ++j) {
            quadrado[j] = aplicar(potencia, potencia[j]);
        }
        potencia = quadrado;
    }
    return estado;
}

struct Bloco {
    long inicio;
    long quantidade;
};

inline Bloco dividir(long n, int rank, int processos) {
    const long base = n / processos;
    const long resto = n % processos;
    return {rank * base + (rank < resto ? rank : resto),
            base + (rank < resto ? 1 : 0)};
}

} // namespace montecarlo

#endif
