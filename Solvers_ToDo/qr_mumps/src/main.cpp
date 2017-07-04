#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <fstream>
#include <sstream>
#include "mpi.h"
#include "abcd_c.h"


void get_Ab(abcd_c *obj, std::string file_A, std::string file_RHS);
void get_MM(std::string file, int &m, int &n, int &nz, double **values, 
        std::vector<int**> indexes, bool is_rhs);

int main(int argc, char* argv[]) {

  int myrank;
  abcd_c *obj;

  int i, j;

  /* Initialize MPI */
  MPI_Init(&argc, &argv);

  /* Find out my identity in the default communicator */
  MPI_Comm_rank(MPI_COMM_WORLD, &myrank);

  obj = new_solver();

  if(myrank == 0) { // the master
    std::string file_A=argv[1];
    std::string file_RHS=argv[2];

    get_Ab(obj, file_A, file_RHS);
    obj->icntl[abcd_verbose_level] = 2;
    obj->icntl[abcd_scaling] = 1;
    obj->icntl[abcd_part_guess] = 0;
    obj->icntl[abcd_part_type] = 3;
    obj->icntl[abcd_part_imbalance] = 2;
    obj->icntl[abcd_nbparts] = 16;
    obj->icntl[abcd_aug_type] = 2;
    obj->icntl[abcd_block_size] = 8;
  }
  call_solver(obj, -1);
  call_solver(obj, 6);

  MPI_Finalize();

  return 0;
}

void get_Ab(abcd_c *obj, std::string file_A, std::string file_RHS) {
    obj->m = 0; // number of rows
    obj->n = 0; // number of columns
    obj->nz = 0; // number of nnz in the lower-triangular part
    obj->sym = 0;
    obj->start_index = 1;

    // allocate the arrays
    obj->irn = NULL;
    obj->jcn = NULL;
    obj->val = NULL;

    get_MM(file_A, obj->m, obj->n, obj->nz, &obj->val, {&obj->irn, &obj->jcn},
        false);
    if (file_RHS == ""){        
        obj->rhs = (double *) malloc(sizeof(double)*(obj->m * obj->nrhs));
        for (int j = 0; j < obj->nrhs; ++j) 
            for (int i = 0; i < obj->m; ++i) 
                obj->rhs[i + j * obj->m] = ((double) i * (j + 1))/obj->m;
    } else
        get_MM(file_RHS, obj->nrhs, obj->nrhs, obj->n, &obj->rhs, {}, true);
}

void get_MM(std::string file, int &m, int &n, int &nz, double **values, 
        std::vector<int**> indexes, bool is_rhs) {
    std::ifstream infile(file.c_str());
    std::cout << "\nGetting matrix in file: " << file << "\n";

    // If we couldn't open the output file stream for reading
    if (!infile) {
        // Print an error and exit
        std::cerr << "Uh oh, " << file << " could not be opened for reading!\n";
        exit(1);
    }

    std::string strInput;
    // Read banner and m, n, nz line
    while (infile) {
        std::getline(infile, strInput);
        std::stringstream stream(strInput);
        // Discard commented lines
        if (strInput[0] == '%') {
            continue;
        }
        // Only read the size if it is present and we are not reading b
        if (!is_rhs) {
            stream >> m;
            stream >> n;
            stream >> nz;
            std::clog << "n: " << n << ", nz: " << nz << "\n";
        }
        break;
    }
    
    // Initialize matrix in 3 arrays
    for(std::vector<int**>::iterator it = indexes.begin(); 
            it != indexes.end(); ++it) {
        **it = new int[nz];
    }
    *values = new double[nz];

    int iii(0);
    // While there's still stuff left to read
    while (infile)
    {
        // each line contains: row column value
        for(std::vector<int**>::iterator it = indexes.begin(); 
                it != indexes.end(); ++it) {
            infile >> *((**it)+iii);
        }
        infile >> *(*values+iii);
        ++iii;
    }
}
