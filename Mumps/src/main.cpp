//! \file main.cpp
//! \brief Mumps resolution of Ax=b
//! \author filou
//! \version 0.1
//! \date 22/10/2016, 18:42
//!
//! Resolution of Ax=b using MUMPS. Details of the parameters:
//!
#include <stdio.h>
#include <string.h>
#include <fstream>
#include <cstdlib>
#include <iostream>
#include <cmath>
#include "dmumps_c.h"
#include "mpi.h"
#include <omp.h>
#include "cmdline.h"

#define ICNTL(I) icntl[(I)-1] /* macro s.t. indices match documentation */
#define CNTL(I) cntl[(I)-1] /* macro s.t. indices match documentation */

void alloc_rhs(double **rhs, int n, int zeros);
void get_A(std::string file, int &n, int &nz, double **values,
        int **irn, int **jcn);
void get_RHS(std::string file, int &n, double **values);


int main (int argc, char **argv) {
    cmdline::parser a;
    a.add<std::string>("matrix", 'A', "Matrix A file", true, "");
    a.add<std::string>("RHS", 'B', "Matrix B file", false, "");
    a.add<int>("zeros", '#', "Number of 0s in RHS after 1s", false, 0);
    a.add<int>("ic01", '1', "output 1", false, 6, cmdline::oneof<int>(0, 6));
    a.add<int>("ic02", '2', "output 2", false, 0, cmdline::oneof<int>(0, 6));
    a.add<int>("ic03", '3', "output 3", false, 6, cmdline::oneof<int>(0, 6));
    a.add<int>("ic04", '4', "output 4", false, 2, cmdline::oneof<int>(0, 1, 2, 3, 4));
    a.add<int>("ic05", '5', "matrix input format", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic06", '6', "P to zero-free diagonal + scale", false, 7, cmdline::oneof<int>(0, 1, 2, 3, 
	4, 5, 6, 7));
    a.add<int>("ic07", '7', "P symmetric for fill-in reduction", false, 7, cmdline::oneof<int>(0, 1, 2, 3, 4, 
	5, 6, 7));
    a.add<int>("ic08", '8', "Scaling", false, 77, cmdline::oneof<int>(-2, -1, 0, 1, 3, 4, 7, 8, 77));
    a.add<int>("ic09", '9', "Transpose", false, 1, cmdline::oneof<int>(0, 1));
    a.add<int>("ic10", '0', "iterative refinement", false, 0, cmdline::oneof<int>(-3, 0, 1));
    a.add<int>("ic11", 'a', "error analysis", false, 0, cmdline::oneof<int>(0, 1, 2));
    a.add<int>("ic12", 'z', "symmetric ordering", false, 0, cmdline::oneof<int>(0, 1, 2, 3));
    a.add<int>("ic13", 'e', "parallelism of root node", false, 0, cmdline::oneof<int>(-1, 0, 1));
    a.add<int>("ic14", 'r', "% relaxation", false, 20);
    a.add<int>("ic18", 't', "distribution", false, 0, cmdline::oneof<int>(0, 1, 2, 3));
    a.add<int>("ic19", 'y', "Schur complement", false, 0, cmdline::oneof<int>(0, 1, 2, 3));
    a.add<int>("ic20", 'u', "format RHS", false, 0, cmdline::oneof<int>(0, 1, 2, 3));
    a.add<int>("ic21", 'i', "distribution solution", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic22", 'o', "out of core", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic23", 'p', "memory size per proc", false, 0);
    a.add<int>("ic24", 'q', "null pivot detection", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic25", 's', "solution deficit matrix + null space basis", false, 0, cmdline::oneof<int>(0, 
	-1));
    a.add<int>("ic26", 'd', "solution phase type for Schur", false, 0, cmdline::oneof<int>(0, 1, 2));
    a.add<int>("ic27", 'f', "block size for nRHS", false, -8);
    a.add<int>("ic28", 'g', "sequential/parallel ordering", false, 0, cmdline::oneof<int>(0, 1, 2));
    a.add<int>("ic29", 'h', "parallel ordering for fill-in reduction", false, 0, cmdline::oneof<int>(0, 1, 2));
    a.add<int>("ic30", 'j', "set of entries of inverse", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic31", 'k', "factors discarded in factorization", false, 0, cmdline::oneof<int>(0, 1, 2));
    a.add<int>("ic32", 'l', "forward elimination in factorization", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic33", 'm', "determinant", false, 0, cmdline::oneof<int>(0, 1));
    a.add<int>("ic35", 'w', "block low rank", false, 0, cmdline::oneof<int>(0, 1));
    a.add<float>("c01", 'x', "relative threashold for numerical pivoting", false, 0.01);
    a.add<float>("c02", 'c', "stopping criterion for iterative refinement", false, -1.0);
    a.add<float>("c03", 'v', "to determine null-pivots", false, 0.0);
    a.add<float>("c04", 'b', "threshold for static pivoting", false, -1.0);
    a.add<float>("c05", 'n', "fixation for null pivots", false, 0.0);
    a.add<float>("c07", '=', "precision of dropping parameter for BLR", false, 0.0);
    
    a.parse_check(argc, argv);
//    bool bn = !cst::TRUE.compare(a.get<std::string>("b_n_present"));

    DMUMPS_STRUC_C id;

    // Initialize MPI
    MPI_Comm comm = MPI_COMM_WORLD;
    MPI_Status status;
    int myid , ierr, nb_procs, namelen=0, val=0;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    ierr = MPI_Init (NULL, NULL);
    ierr = MPI_Comm_size(comm, &nb_procs);
    ierr = MPI_Comm_rank(comm, &myid);
    ierr = MPI_Get_processor_name(processor_name, &namelen);
    std::clog << "MPI initialization in Mumps, error code: " << ierr << "\n";

    if (myid != 0)
        MPI_Recv(&val, 1, MPI_INTEGER, myid-1, 0, comm, &status);
    std::cout << "MPI_proc\tSize\tCPU\tProcessor\n";
    std::cout << myid << "\t" << nb_procs << "\t" << sched_getcpu() << "\t" << processor_name << "\n";
    // Display initialized OpenMP
    int tid, nthreads;
    std::cout << "MPI_proc\tOMP_thread\tSize\tCPU\n";
        #pragma omp parallel
        {
                tid = omp_get_thread_num();
                nthreads = omp_get_num_threads();
                #pragma omp critical
                {
                        std::cout << myid << "\t" << tid << "\t" << nthreads << "\t" << sched_getcpu() << "\n";
                }
        }
    if (nb_procs != 1) {
        if (myid==0)
                MPI_Send(&val, 1, MPI_INTEGER, 1, 0, comm);
        else {
                MPI_Send(&val, 1, MPI_INTEGER, (myid+1)%nb_procs, 0, comm);
        }
        MPI_Barrier(MPI::COMM_WORLD);
    }

    /* Initialize a MUMPS instance . Use MPI_COMM_WORLD . */
    std::cout << "MUMPS initialization\n";
    id.sym = 0;	// unsymetric
    id.par = 1;	// working host
    id.comm_fortran = -987654;	// MPI_COMM_WORLD
    id.job = -1;	// Initialization
    dmumps_c(&id);

    if(myid==0) {
	int k;
        std::string arg;
	// Set controls
        int opt=0;
        for(k=1; k<36; ++k) {
    	    if (k==34 || (k>14 && k<18))
		    continue;
	    arg="ic";
	    if (k<10)
		    arg+="0";
	    arg+=std::to_string(static_cast<long long>(k));
            opt=a.get<int>(arg);
	    id.ICNTL(k)=opt;
        }

	// Set constants
        float fopt=0;
        for(k=1; k<8; ++k) {
    	    if (k==6)
		    continue;
	    arg="c";
	    if (k<10)
		    arg+="0";
	    arg+=std::to_string(static_cast<long long>(k));
            fopt=a.get<float>(arg);
	    id.CNTL(k)=opt;
        }

	// Read A
        std::string A_file = a.get<std::string>("matrix");
        get_A(A_file, id.n, id.nz, &id.a, &id.irn, &id.jcn);
	for(int iii=0; iii<10; ++iii)
		std::cout << id.irn[iii] << "\t" << id.jcn[iii] << "\t" << id.a[iii] << "\n";

	// Allocate RHS
        id.lrhs = id.n;
        id.nrhs = 1;
        std::string b_file = a.get<std::string>("RHS");
	if (b_file=="") {
                int zeros=a.get<int>("zeros");
		alloc_rhs(&id.rhs, id.lrhs, zeros);
	} else
	        get_RHS(b_file, id.lrhs, &id.rhs);
    }

    // Call MUMPS solver
    id.job = 6;	// Analysis+Facto+Solve
    dmumps_c(&id);

    // Terminate instance
    id.job = -2;
    dmumps_c(&id);
    ierr = MPI_Finalize();

    // Free arrays
    delete[] id.a;
    delete[] id.irn;
    delete[] id.jcn;
    delete[] id.rhs;

    return 0;
}


void get_A(std::string file, int &n, int &nz, double **values,
        int **irn, int **jcn) {
    std::ifstream infile(file.c_str());
    std::cout << "Getting matrix in file: " << file << "\n";

    // If we couldn't open the output file stream for reading
    if (!infile)
    {
     	// Print an error and exit
        std::cerr << "Uh oh, " << file << " could not be opened for reading!\n";
        exit(1);
    }

    std::string strInput;
    // We do not need the two first commented lines
    for(int cl(0); cl < 2; ++cl) {
        std::getline(infile, strInput);
    }

    // First line is: N N NZ
    infile >> n;
    infile >> n;
    infile >> nz;

    std::cout << "Matrix of size n: " << n << ", nz: " << nz << "\n";

    *irn = new int[nz];
    *jcn = new int[nz];
    *values = new double[nz];

    // While there's still stuff left to read
    int iii(0);
    while (infile)
    {
	infile >> *(*irn+iii);
	infile >> *(*jcn+iii);
	infile >> *(*values+iii);
        ++iii;
    }
//    std::cout << iii;
}

void get_RHS(std::string file, int &n, double **values) {
    std::ifstream infile(file.c_str());
    std::cout << "Getting matrix in file: " << file << "\n";

    // If we couldn't open the output file stream for reading
    if (!infile)
    {
     	// Print an error and exit
        std::cerr << "Uh oh, " << file << " could not be opened for reading!\n";
        exit(1);
    }

    std::string strInput;
    // We do not need the two first commented lines
    for(int cl(0); cl < 2; ++cl) {
        std::getline(infile, strInput);
    }

    int nrhs=0;
    infile >> n;
    infile >> nrhs;

    *values = new double[n];

    // While there's still stuff left to read
    int iii(0);
    while (infile)
    {
        infile >> *(*values+iii);
        ++iii;
    }
}


void alloc_rhs(double **rhs, int n, int zeros) {
    std::cout << "Allocating RHS full of 1.0 and of size: " << n << "\n";
    *rhs = new double[n];
    int iii;
    for(iii = 0; iii < n-zeros; iii++) *(*rhs+iii) = 1.0;
    for(iii = n-zeros; iii < n; iii++) *(*rhs+iii) = 0.0;
}
