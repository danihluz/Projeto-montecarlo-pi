/* baseline/02_montecarlo_pi_perfilamento.cpp
 * Copia instrumentada de baseline/02_montecarlo_pi.cpp para fins de
 * perfilamento (Issue #3). A logica do algoritmo (gerador xorshift,
 * semente, teste x*x+y*y<=1, calculo de pi) NAO foi alterada em
 * nenhum ponto. O baseline original ja media internamente o tempo do
 * laco principal (t0/t1); a unica adicao aqui e um par de marcas de
 * tempo ao redor de TUDO dentro de main, para obter o tempo total do
 * programa e, por diferenca, o tempo gasto fora do laco (leitura de
 * argv, inicializacao, calculo final).
 *
 * Compilar: g++ -O2 -o baseline/02_montecarlo_pi_perfilamento baseline/02_montecarlo_pi_perfilamento.cpp
 * Executar: ./baseline/02_montecarlo_pi_perfilamento 50000000
 */
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <ctime>

static double agora() {
    timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

static inline uint64_t xorshift(uint64_t& s) {
    s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s;
}

int main(int argc, char** argv) {
    double t_prog_inicio = agora();           // ADICIONADO: inicio do programa

    long n = (argc > 1) ? atol(argv[1]) : 50000000L;
    uint64_t s = 88172645463325252ULL;
    long dentro = 0;

    double t0 = agora();                       // igual ao baseline original
    for (long i = 0; i < n; i++) {
        double x = (xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
        double y = (xorshift(s) >> 11) * (1.0 / 9007199254740992.0);
        if (x*x + y*y <= 1.0) dentro++;
    }
    double pi = 4.0 * (double)dentro / (double)n;
    double t1 = agora();                        // igual ao baseline original

    double t_prog_fim = agora();                // ADICIONADO: fim do programa (antes do printf)

    double tempo_laco   = t1 - t0;
    double tempo_total  = t_prog_fim - t_prog_inicio;
    double tempo_outros = tempo_total - tempo_laco;

    // Mesma saida do baseline original, para nao mudar o formato esperado
    printf("n=%ld  pi=%.6f  dentro=%ld  tempo=%.6f s\n", n, pi, dentro, t1 - t0);

    // Saida extra de perfilamento, em stderr para nao misturar com a saida principal
    fprintf(stderr,
        "PERFIL,n=%ld,tempo_total_s=%.6f,tempo_laco_s=%.6f,tempo_outros_s=%.6f\n",
        n, tempo_total, tempo_laco, tempo_outros);

    return 0;
}