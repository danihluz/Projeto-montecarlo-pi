// scripts/analisar.cpp
// Le dados/medicoes.csv, calcula medianas, speedup e eficiencia e grava:
//   <saida>/resumo.csv                   (todas as configuracoes, formato longo)
//   <saida>/tabela_forte_n<N>.csv        (uma por n; pronta para virar grafico)
//   <saida>/tabela_fraca.csv             (escalabilidade fraca)
// Compilar: g++ -O2 -std=c++17 -o scripts/analisar scripts/analisar.cpp
// Executar: ./scripts/analisar [entrada.csv] [pasta_de_saida]   (na raiz do repositorio)
//   padrao: entrada = dados/medicoes.csv, pasta_de_saida = dados
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using Chave = std::tuple<std::string, std::string, long, int>;  // versao, escala, n, workers

static const long N_POR_WORKER = 12500000L;  // igual ao de coletar.sh

static void erro(const std::string& msg) {
    std::cerr << "ERRO: " << msg << "\n";
    std::exit(1);
}

static std::vector<std::string> dividir(const std::string& linha) {
    std::vector<std::string> campos;
    std::stringstream ss(linha);
    std::string c;
    while (std::getline(ss, c, ',')) campos.push_back(c);
    return campos;
}

static double mediana(std::vector<double> v) {
    std::sort(v.begin(), v.end());
    size_t m = v.size() / 2;
    return (v.size() % 2) ? v[m] : (v[m - 1] + v[m]) / 2.0;
}

// valores negativos significam "nao disponivel" e viram campo vazio
static std::string campo(double x) {
    if (x < 0) return "";
    char buf[64];
    std::snprintf(buf, sizeof buf, "%.6f", x);
    return buf;
}

int main(int argc, char** argv) {
    std::string entrada = (argc > 1) ? argv[1] : "dados/medicoes.csv";
    std::string dir = (argc > 2) ? argv[2] : "dados";
    std::filesystem::create_directories(dir);
    std::ifstream in(entrada);
    if (!in) erro("nao consegui abrir " + entrada);

    // 1) leitura e validacao: qualquer linha que nao seja OK interrompe a analise
    std::map<Chave, std::vector<double>> tempos;
    std::string linha;
    std::getline(in, linha);  // cabecalho
    int numero = 1;
    try {
        while (std::getline(in, linha)) {
            numero++;
            if (!linha.empty() && linha.back() == '\r') linha.pop_back();
            if (linha.empty()) continue;
            auto c = dividir(linha);
            if (c.size() != 9)
                erro("linha " + std::to_string(numero) + " tem " + std::to_string(c.size()) + " campos (esperado 9)");
            if (c[8] != "OK")
                erro("linha " + std::to_string(numero) + " com status_validacao=" + c[8] + "; corrija antes de analisar");
            tempos[Chave(c[0], c[1], std::stol(c[2]), std::stoi(c[3]))].push_back(std::stod(c[5]));
        }
    } catch (const std::exception&) {
        erro("valor numerico invalido na linha " + std::to_string(numero));
    }
    if (tempos.empty()) erro(entrada + " nao tem medicoes");

    // 2) medianas
    std::map<Chave, double> med;
    for (auto& kv : tempos) med[kv.first] = mediana(kv.second);
    auto achar = [&](const std::string& v, const std::string& e, long n, int p) -> double {
        auto it = med.find(Chave(v, e, n, p));
        return it == med.end() ? -1.0 : it->second;
    };

    // 3) resumo.csv (formato longo)
    std::ofstream resumo(dir + "/resumo.csv");
    if (!resumo) erro("nao consegui criar " + dir + "/resumo.csv");
    resumo << "versao,escala,n,workers,tempo_mediano_s,speedup_vs_seq,eficiencia_vs_seq,"
              "speedup_vs_1worker,eficiencia_vs_1worker,eficiencia_fraca\n";
    for (auto& kv : med) {
        const std::string& v = std::get<0>(kv.first);
        const std::string& esc = std::get<1>(kv.first);
        long n = std::get<2>(kv.first);
        int p = std::get<3>(kv.first);
        double t = kv.second;
        double seq = achar("sequencial", esc, n, 1);
        double t1 = achar(v, esc, n, 1);
        double s_seq = (seq > 0) ? seq / t : -1;
        double e_seq = (s_seq > 0) ? s_seq / p : -1;
        double s_t1 = (esc == "forte" && t1 > 0) ? t1 / t : -1;
        double e_t1 = (s_t1 > 0) ? s_t1 / p : -1;
        double e_fraca = -1;
        if (esc == "fraca" && v != "sequencial") {
            double base = achar(v, "fraca", N_POR_WORKER, 1);
            if (base > 0) e_fraca = base / t;
        }
        resumo << v << ',' << esc << ',' << n << ',' << p << ',' << campo(t) << ',' << campo(s_seq) << ','
               << campo(e_seq) << ',' << campo(s_t1) << ',' << campo(e_t1) << ',' << campo(e_fraca) << '\n';
    }
    std::cout << "Gravado " << dir << "/resumo.csv\n";

    // 4) tabelas largas da escalabilidade forte (uma por n)
    std::set<long> ns;
    for (auto& kv : med)
        if (std::get<1>(kv.first) == "forte") ns.insert(std::get<2>(kv.first));
    for (long n : ns) {
        std::set<int> ws;
        for (auto& kv : med)
            if (std::get<1>(kv.first) == "forte" && std::get<2>(kv.first) == n && std::get<0>(kv.first) != "sequencial")
                ws.insert(std::get<3>(kv.first));
        if (ws.empty()) continue;
        double seq = achar("sequencial", "forte", n, 1);
        if (seq <= 0) { std::cerr << "AVISO: sem sequencial para n=" << n << " (forte); tabela ignorada\n"; continue; }
        std::string nome = dir + "/tabela_forte_n" + std::to_string(n) + ".csv";
        std::ofstream o(nome);
        if (!o) erro("nao consegui criar " + nome);
        o << "workers,tempo_sequencial,tempo_openmp,tempo_mpi,speedup_openmp,speedup_mpi,speedup_ideal,"
             "eficiencia_openmp,eficiencia_mpi,eficiencia_ideal\n";
        for (int p : ws) {
            double to = achar("openmp", "forte", n, p), tm = achar("mpi", "forte", n, p);
            o << p << ',' << campo(seq) << ',' << campo(to) << ',' << campo(tm) << ','
              << campo(to > 0 ? seq / to : -1) << ',' << campo(tm > 0 ? seq / tm : -1) << ',' << p << ','
              << campo(to > 0 ? seq / to / p : -1) << ',' << campo(tm > 0 ? seq / tm / p : -1) << ",1\n";
        }
        std::cout << "Gravado " << nome << "\n";
    }

    // 5) tabela larga da escalabilidade fraca (n = N_POR_WORKER * p)
    std::set<int> wf;
    for (auto& kv : med)
        if (std::get<1>(kv.first) == "fraca" && std::get<0>(kv.first) != "sequencial") wf.insert(std::get<3>(kv.first));
    if (!wf.empty()) {
        double bo = achar("openmp", "fraca", N_POR_WORKER, 1), bm = achar("mpi", "fraca", N_POR_WORKER, 1);
        std::ofstream o(dir + "/tabela_fraca.csv");
        if (!o) erro("nao consegui criar " + dir + "/tabela_fraca.csv");
        o << "workers,n,tempo_openmp,tempo_mpi,eficiencia_fraca_openmp,eficiencia_fraca_mpi,eficiencia_ideal\n";
        for (int p : wf) {
            long n = N_POR_WORKER * p;
            double to = achar("openmp", "fraca", n, p), tm = achar("mpi", "fraca", n, p);
            o << p << ',' << n << ',' << campo(to) << ',' << campo(tm) << ','
              << campo(to > 0 && bo > 0 ? bo / to : -1) << ',' << campo(tm > 0 && bm > 0 ? bm / tm : -1) << ",1\n";
        }
        std::cout << "Gravado " << dir << "/tabela_fraca.csv\n";
    }
    return 0;
}