#####################################
## DIRECTORIES
#####################################
SRC = src
DISTR = distr
BUILD = build
EXEC = mumps_test
OUTPUT = output_folder
DISTR_ARCHIVE = distr_archive

#####################################
## COMPILER
#####################################
CC = mpiicpc
LD = mpiicpc
CFLAGS=-c -O2 -Wall $(IMUMPS) -std=c++11 -MMD -MP -qopenmp
LDFLAGS=$(LMUMPS) $(LSCOTCH) $(LPARMETIS) $(LMETIS) $(LSCALAPACK) $(LBLAS) $(LIOMP) -std=c++11 -qopenmp -lifcore

#####################################
## LIBRARIES
#####################################
#############
# MUMPS
#############
#MUMPS_HOME=/homea/eocoe/eocoe26/lib/MUMPS_5.1.1
#IMUMPS= -I$(MUMPS_HOME)/include
#LMUMPS= -L$(MUMPS_HOME)/lib -lcmumps -lsmumps -ldmumps -lzmumps -lmumps_common -lpord
LMUMPS= -lcmumps -lsmumps -ldmumps -lzmumps -lmumps_common -lpord
#############
# METIS
#############
LMETIS=-lmetis
LPARMETIS= -lparmetis
#############
# METIS
#############
#SCOTCHDIR  = /usr/local/software/jureca/Stages/2016b/software/SCOTCH/6.0.4-iimpi-2016b/
#ISCOTCH    = -I$(SCOTCHDIR)/include
#LSCOTCH    = -L$(SCOTCHDIR)/lib -lesmumps -lscotch -lscotcherr -lscotcherrexit -lptesmumps -lptscotch -lptscotcherr -lptscotcherrexit
LSCOTCH    = -lesmumps -lscotch -lscotcherr -lscotcherrexit -lptesmumps -lptscotch -lptscotcherr -lptscotcherrexit
#############
# SCALAPACK
#############
LSCALAPACK= -lmkl_scalapack_lp64 -lmkl_blacs_intelmpi_lp64
#############
# BLAS
#############
LBLAS = -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core
#############
# INTEL OPENMP
#############
LIOMP=-L/usr/local/software/jureca/Stages/2016b/software/icc/2017.0.098-GCC-5.4.0/lib/intel64 -liomp5
