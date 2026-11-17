CXX = g++
MPICXX = mpic++
CXXFLAGS = -O2

.PHONY: all testar-jump clean

all: 02_montecarlo_pi_mpi

02_montecarlo_pi_mpi: 02_montecarlo_pi_mpi.cpp montecarlo.hpp
	$(MPICXX) $(CXXFLAGS) -o $@ $<

teste_jump_ahead: teste_jump_ahead.cpp montecarlo.hpp ../baseline/02_montecarlo_pi.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

testar-jump: teste_jump_ahead
	./teste_jump_ahead

clean:
	rm -f 02_montecarlo_pi_mpi teste_jump_ahead
