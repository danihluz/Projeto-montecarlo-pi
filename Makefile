CXX := g++
MPICXX := mpic++
CXXFLAGS := -O2

BASELINE_SRC := baseline/02_montecarlo_pi.cpp
BASELINE_BIN := baseline/02_montecarlo_pi
PERFIL_SRC := baseline/02_montecarlo_pi_perfilamento.cpp
PERFIL_BIN := baseline/02_montecarlo_pi_perfilamento
OPENMP_SRC := openmp/02_montecarlo_pi_openmp.cpp
OPENMP_BIN := openmp/02_montecarlo_pi_omp
MPI_SRC := mpi/02_montecarlo_pi_mpi.cpp
MPI_BIN := mpi/02_montecarlo_pi_mpi

.PHONY: all baseline openmp mpi perfilamento clean

all: baseline openmp mpi

baseline: $(BASELINE_BIN)

$(BASELINE_BIN): $(BASELINE_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

openmp: $(OPENMP_BIN)

$(OPENMP_BIN): $(OPENMP_SRC) openmp/xorshift_jump.h
	$(CXX) $(CXXFLAGS) -fopenmp -o $@ $<

mpi: $(MPI_BIN)

$(MPI_BIN): $(MPI_SRC) mpi/montecarlo.hpp
	$(MPICXX) $(CXXFLAGS) -o $@ $<

perfilamento: $(PERFIL_BIN)

$(PERFIL_BIN): $(PERFIL_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f $(BASELINE_BIN) $(PERFIL_BIN) $(OPENMP_BIN) $(MPI_BIN)
