
#####################################
## DIRECTORIES
#####################################
SRC = src
DISTR = distr
BUILD = build
EXEC = abcd_run
OUTPUT = output_folder
DISTR_ARCHIVE = distr_archive
LIB_HOME=/scratch/algo/leleux/lib_intel
INTELROOT=/data/softs/intel/compilers_and_libraries_2017/linux
MKLROOT=$(INTELROOT)/mkl/lib/intel64

#####################################
## COMPILER
#####################################
CC=mpiicpc
LD=mpiicpc
CFLAGS=-c -O3 -Wall -DNDEBUG $(IABCD) $(IMUMPS) $(IPARMETIS) $(IMETIS) $(ISCOTCH) $(ISUITESPARSE) $(IBOOST) $(IPATOH) $(IHWLOC) $(ISPARSELIB) $(COTHERS)
LDFLAGS=-O3 -DNDEBUG -z muldefs $(LABCD) $(LMUMPS) $(LSCOTCH) $(LPTSCOTCH) $(LPARMETIS) $(LMETIS) $(LPATOH) $(LSPARSELIB) $(LSUITESPARSE) $(LCOLAMD) $(LSCALAPACK) $(LLAPACK) $(LBLAS) $(LHWLOC) $(LIOMP) $(LBOOST) $(LPYTHON) $(LOTHERS)

#####################################
## LIBRARIES
#####################################
#############
# ABCD
#############
ABCD_HOME=$(LIB_HOME)/abcd_dev/
IABCD= -I$(ABCD_HOME)/include
LABCD= -L$(ABCD_HOME)/build/lib -labcd
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
IMETIS= -I$(METIS_HOME)/include
LMETIS= -L$(METIS_HOME)/lib -lmetis
PARMETIS_HOME=$(LIB_HOME)/parmetis-4.0.3/build
IPARMETIS= -I$(PARMETIS_HOME)/include
LPARMETIS= -L$(PARMETIS_HOME)/lib -lparmetis
#############
# SCOTCH
#############
SCOTCH_HOME=$(LIB_HOME)/scotch_6.0.4_2015
ISCOTCH= -I$(SCOTCH_HOME)/include
LSCOTCH= -L$(SCOTCH_HOME)/lib -lesmumps -lscotch -lscotcherr -lscotcherrexit -lscotchmetis
LPTSCOTCH= -lptesmumps -lptscotch -lptscotcherr -lptscotcherrexit -lptscotchparmetis
#############
# SCALAPACK
#############
LSCALAPACK= -L$(MKLROOT) -lmkl_scalapack_lp64 -lmkl_blacs_intelmpi_lp64
#############
# BLAS
#############
LBLAS= -L$(MKLROOT) -lmkl_gf_lp64 -lmkl_gnu_thread -lmkl_core
#############
# SUITESPARSE
#############
SUITESPARSE_HOME=$(LIB_HOME)/SuiteSparse
ISUITESPARSE= -I$(SUITESPARSE_HOME)/include
LSUITESPARSE= -L$(SUITESPARSE_HOME)/lib -lsuitesparseconfig
LCOLAMD= -lcolamd
#############
# BOOST
#############
BOOST_HOME=$(LIB_HOME)/boost_1_63_0/build
IBOOST= -I$(BOOST_HOME)/include
LBOOST= -L$(BOOST_HOME)/lib -lboost_mpi -lboost_serialization
#############
# PATOH
#############
PATOH_HOME=$(LIB_HOME)/patoh/Linux-x86_64
IPATOH= -I$(PATOH_HOME)
LPATOH= -L$(PATOH_HOME) -lpatoh
#############
# PYTHON
#############
PYTHON_HOME=$(LIB_HOME)/Python-2.7/build
IPYTHON= -I$(PYTHON_HOME)/include/python2.7
LPYTHON= -L$(PYTHON_HOME)/lib
#############
# HWLOC
#############
HWLOC_HOME=$(LIB_HOME)/hwloc-1.11.7/build
IHWLOC= -I$(HWLOC_HOME)/include
LHWLOC= -L$(HWLOC_HOME)/lib -lhwloc
#############
# SPARSELIB
#############
SPARSELIB_HOME=$(ABCD_HOME)/lib/sparselib
ISPARSELIB= -I$(SPARSELIB_HOME)/include
LSPARSELIB= -L$(SPARSELIB_HOME)/lib -lmv -lsparse -lspblas
#############
# OTHERS
#############
COTHERS= -std=c++14 -qopenmp -fPIC -MMD -MP
LOTHERS= -std=c++14 -qopenmp -fPIC -lpthread -lm -lifcore
