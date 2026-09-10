CXX := g++
CXXFLAGS := -O2

BASELINE_SRC := baseline/02_montecarlo_pi.cpp
BASELINE_BIN := baseline/02_montecarlo_pi
PERFIL_SRC := baseline/02_montecarlo_pi_perfilamento.cpp
PERFIL_BIN := baseline/02_montecarlo_pi_perfilamento

.PHONY: all baseline perfilamento clean

all: baseline

baseline: $(BASELINE_BIN)

$(BASELINE_BIN): $(BASELINE_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

perfilamento: $(PERFIL_BIN)

$(PERFIL_BIN): $(PERFIL_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f $(BASELINE_BIN) $(PERFIL_BIN)
