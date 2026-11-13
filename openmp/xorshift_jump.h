#ifndef OPENMP_XORSHIFT_JUMP_H
#define OPENMP_XORSHIFT_JUMP_H

#include <cstdint>

namespace montecarlo {

// Mesma transicao do baseline, com aritmetica sem sinal de 64 bits.
static inline uint64_t xorshift(uint64_t& s) {
    s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s;
}

// As colunas guardam a imagem dos 64 vetores da base de GF(2)^64.
// powers_[k] representa T^(2^k), onde T e a transicao xorshift.
class JumpAhead {
    uint64_t powers_[64][64];

    static uint64_t aplicar(const uint64_t* colunas, uint64_t estado) {
        uint64_t resultado = 0;
        for (unsigned bit = 0; estado != 0; ++bit, estado >>= 1) {
            if (estado & 1ULL) resultado ^= colunas[bit];
        }
        return resultado;
    }

public:
    // Prepara somente as potencias necessarias. Custo O(64^2 log max_passos),
    // memoria fixa de 32 KiB; depois da construcao, a tabela e so de leitura.
    explicit JumpAhead(uint64_t max_passos) {
        if (max_passos == 0) return;
        for (unsigned bit = 0; bit < 64; ++bit) {
            uint64_t base = 1ULL << bit;
            powers_[0][bit] = xorshift(base);
        }
        for (unsigned k = 1; (max_passos >>= 1) != 0; ++k) {
            for (unsigned bit = 0; bit < 64; ++bit) {
                powers_[k][bit] = aplicar(powers_[k - 1], powers_[k - 1][bit]);
            }
        }
    }

    // Precondicao: passos <= max_passos usado na construcao.
    // T^passos(s), em O(64 log passos), sem percorrer o prefixo da sequencia.
    uint64_t avancar(uint64_t estado, uint64_t passos) const {
        for (unsigned k = 0; passos != 0; ++k, passos >>= 1) {
            if (passos & 1ULL) estado = aplicar(powers_[k], estado);
        }
        return estado;
    }
};

struct Bloco {
    long inicio;
    long fim;
};

// Precondicoes: n >= 0, p > 0, 0 <= tid < p.
// Os primeiros n%p blocos recebem um ponto extra. Evita calcular n*tid,
// que poderia transbordar mesmo quando os limites finais cabem em long.
inline Bloco bloco_contiguo(long n, int tid, int p) {
    const long quociente = n / p;
    const long resto = n % p;
    const long inicio = tid * quociente + (tid < resto ? tid : resto);
    return {inicio, inicio + quociente + (tid < resto ? 1 : 0)};
}

}  // namespace montecarlo

#endif
