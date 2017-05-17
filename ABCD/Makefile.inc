#####################################
## LIBRARIES
#####################################
MKLROOT=/usr/local/software/jureca/Stages/2016b/software/imkl/2017.0.098-iimpi-2016b/mkl
#############
# MUMPS
#############
MUMPS_HOME=/homea/eocoe/eocoe26/lib/MUMPS_5.1.1
IMUMPS= -I$(MUMPS_HOME)/include
LMUMPS= -L$(MUMPS_HOME)/lib -lcmumps -lsmumps -ldmumps -lzmumps -lmumps_common -lpord
#############
# METIS
#############
METIS_HOME=/usr/local/software/jureca/Stages/2016b/software/METIS/5.1.0-iccifort-2017.0.098-GCC-5.4.0/
IMETIS= -I$(METIS_HOME)/include
LMETIS= -L$(METIS_HOME)/lib -lmetis
PARMETIS_HOME=/usr/local/software/jureca/Stages/2016b/software/ParMETIS/4.0.3-iimpi-2016b/
IPARMETIS= -I$(PARMETIS_HOME)/include
LPARMETIS= -L$(PARMETIS_HOME)/lib -lparmetis
#############
# SCOTCH
#############
#SCOTCH_HOME=/usr/local/software/jureca/Stages/2016b/software/SCOTCH/6.0.4-iimpi-2016b/
#ISCOTCH= -I$(SCOTCH_HOME)/include
#LSCOTCH= -L$(SCOTCH_HOME)/lib -lesmumps -lscotch -lscotcherr -lscotcherrexit
#LPTSCOTCH= -lptesmumps -lptscotch -lptscotcherr -lptscotcherrexit
#############
# SCALAPACK
#############
LSCALAPACK= -L$(MKLROOT) -lmkl_scalapack_lp64 -lmkl_blacs_intelmpi_lp64
#############
# BLAS
#############
LBLAS = -L$(MKLROOT) -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core
#############
# INTEL OPENMP
#############
LIOMP=-L/usr/local/software/jureca/Stages/2016b/software/icc/2017.0.098-GCC-5.4.0/lib/intel64 -liomp5
#############
# ABCD
#############
ABCD_HOME=/homea/eocoe/eocoe26/lib/abcd/
IABCD=-I$(ABCD_HOME)/include -I$(ABCD_HOME)/lib/sparselib/mv/include/ -I$(ABCD_HOME)/lib/sparselib/include
LABCD=-L$(ABCD_HOME)/build/lib/ -labcd -L$(ABCD_HOME)/lib/sparselib/lib/ -lmv -lsparse -lspblas
#############
# HWLOC
#############
HWLOC_HOME=/homea/eocoe/eocoe26/lib/hwloc-1.11.7rc1/build/
IHWLOC=-I$(HWLOC_HOME)/include/
LHWLOC=-L$(HWLOC_HOME)/lib/ -lhwloc
#############
# BOOST
#############
BOOST_HOME=/homea/eocoe/eocoe26/lib/boost_1_63_0/build
IBOOST=-I$(BOOST_HOME)/include/boost
LBOOST=-L$(BOOST_HOME)/lib -lboost_mpi -lboost_serialization
#############
# PATOH
#############
PATOH_HOME=/homea/eocoe/eocoe26/lib/patoh/Linux-x86_64/
IPATOH=-I$(PATOH_HOME)
LPATOH=-L$(PATOH_HOME) -lpatoh

#####################################
## COMPILER
#####################################
CC=mpiicpc
LD=mpiicpc
CFLAGS=-c -O2 -Wall -std=c++11 $(IABCD) $(IQRMUMPS) $(ISTARPU) $(IMETIS) $(ISCOTCH) $(IMUMPS) $(IOMPI) $(IPARMETIS) $(ICOLAMD) $(ISUITESPARSE) $(IBOOST) $(IPATOH) $(IHWLOC) -MMD -MP -qopenmp -m64 -DNDEBUG
LDFLAGS=$(LABCD) $(LQRMUMPS) $(LSTARPU) $(LMUMPS) $(LPATOH) $(LSCOTCH) $(LPTSCOTCH) $(LPARMETIS) $(LMETIS) $(LSUITESPARSE) $(LCOLAMD) $(LSCALAPACK) $(LBLAS) $(LOMPI) $(LIOMP) $(LBOOST) $(LHWLOC) -std=c++11 -qopenmp -lifcore -z muldefs -m64 -DNDEBUG
