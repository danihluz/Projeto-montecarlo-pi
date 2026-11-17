// scripts/amdahl.cpp
// Calcula S(p) = 1 / ((1 - f) + f / p) a partir de dados/perfilamento.csv.
// Compilar: g++ -O2 -std=c++17 -o scripts/amdahl scripts/amdahl.cpp
// Executar: ./scripts/amdahl            (rodar na raiz do repositorio)
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    const std::vector<int> ps = {1, 2, 4, 6, 8, 12};

    std::ifstream in("dados/perfilamento.csv");
    if (!in) { std::cerr << "ERRO: nao consegui abrir dados/perfilamento.csv\n"; return 1; }
    std::ofstream out("dados/amdahl.csv");
    if (!out) { std::cerr << "ERRO: nao consegui criar dados/amdahl.csv\n"; return 1; }
    out << "n,f,p,speedup_amdahl\n";

    std::string linha;
    std::getline(in, linha);  // cabecalho: n,trecho,tempo_s,percentual
    int lidas = 0;
    while (std::getline(in, linha)) {
        if (!linha.empty() && linha.back() == '\r') linha.pop_back();
        std::stringstream ss(linha);
        std::string n, trecho, tempo, perc;
        std::getline(ss, n, ','); std::getline(ss, trecho, ',');
        std::getline(ss, tempo, ','); std::getline(ss, perc, ',');
        if (trecho != "trecho_principal") continue;
        double f = std::atof(perc.c_str()) / 100.0;
        lidas++;
        for (int p : ps) {
            double s = 1.0 / ((1.0 - f) + f / p);
            char buf[160];
            std::snprintf(buf, sizeof buf, "%s,%.6f,%d,%.4f\n", n.c_str(), f, p, s);
            out << buf;
            std::printf("n=%10s  f=%.6f  p=%2d  S(p)=%.4f\n", n.c_str(), f, p, s);
        }
    }
    if (lidas == 0) { std::cerr << "ERRO: nenhuma linha 'trecho_principal' em perfilamento.csv\n"; return 1; }
    std::printf("Gravado em dados/amdahl.csv\n");
    return 0;
}