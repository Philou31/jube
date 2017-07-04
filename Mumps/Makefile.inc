#####################################
## DIRECTORIES
#####################################
SRC = src
DISTR = distr
BUILD = build
EXEC = mumps_test
OUTPUT = output_folder
DISTR_ARCHIVE = distr_archive
LIB_HOME = /scratch/algo/leleux/lib_intel/
MKL_HOME = /data/softs/intel/compilers_and_libraries_2017/linux/mkl

#####################################
## COMPILER
#####################################
CC = mpiicpc
LD = mpiicpc
CFLAGS=-c -O2 -Wall $(IMUMPS) -std=c++11 -MMD -MP -qopenmp -fPIC
LDFLAGS=$(LMUMPS) $(LSCOTCH) $(LPARMETIS) $(LMETIS) $(LSCALAPACK) $(LBLAS) $(LIOMP) -std=c++11 -qopenmp -lifcore -fPIC

#####################################
## LIBRARIES
#####################################
#############
# MUMPS
#############
MUMPS_HOME=$(LIB_HOME)/MUMPS_5.1.1
IMUMPS= -I$(MUMPS_HOME)/include
LMUMPS= -L$(MUMPS_HOME)/lib -lcmumps -lsmumps -ldmumps -lzmumps -lmumps_common -lpord
#############
# METIS
#############
METIS_HOME=$(LIB_HOME)/metis-5.1.0/build
PARMETIS_HOME=$(LIB_HOME)/parmetis-4.0.3/build
LMETIS= -L$(METIS_HOME)/lib -lmetis
LPARMETIS= -L$(PARMETIS_HOME)/lib -lparmetis
#############
# SCOTCH
#############
SCOTCHDIR  = $(LIB_HOME)/scotch_6.0.4_2015
ISCOTCH    = -I$(SCOTCHDIR)/include
LSCOTCH    = -L$(SCOTCHDIR)/lib -lesmumps -lscotch -lscotcherr -lscotcherrexit -lptesmumps -lptscotch -lptscotcherr -lptscotcherrexit
#############
# SCALAPACK
#############
LSCALAPACK= -L$(MKL_HOME)/lib/intel64/ -lmkl_scalapack_lp64 -lmkl_blacs_intelmpi_lp64
#############
# BLAS
#############
LBLAS = -L$(MKL_HOME)/lib/intel64/ -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core
#############
# INTEL OPENMP
#############
LIOMP= -liomp5
