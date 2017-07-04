#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <fstream>
#include <sstream>
#include "mpi.h"
#include "abcd_c.h"
#include "cmdline.h"


void get_Ab(abcd_c *obj, std::string file_A, std::string file_RHS, int zeros);
void get_MM(std::string file, int &m, int &n, int &nz, double **values, 
        std::vector<int**> indexes, bool is_rhs);

int main(int argc, char* argv[]) {
    cmdline::parser a;
    a.add<std::string>("matrix", 'A', "Matrix A file", true, "");
    a.add<std::string>("RHS", 'B', "Matrix B file", false, "");
    a.add<int>("zeros", 'a', "Number of zeros at first in RHS, then all 1s", false, 0);
    a.add<int>("nbparts", 'z', "Number of partitions (8)", false, 8);
    a.add<int>("part_type", 'e', "Partitioning type (1 manual, 2 uniform def, 3 patoh->imbalance)", false, 2);
    a.add<int>("part_guess", 'r', "Guess number of partitions (0,1)", false, 0);
    a.add<int>("scaling", 't', "Activate scaling (0,1)", false, 0);
    a.add<int>("itmax", 'y', "Maximum number of iterations (1000)", false, 1000);
    a.add<int>("block_size", 'u', "Size of the blocks for Block-CG (1)", false, 1);
    a.add<int>("verbose_level", 'i', "Verbose level (2)", false, 2);
    a.add<int>("aug_type", 'o', "Augmentation type (0 def bc, 1 Cij aug, 2 Aij aug)", false, 0);
    a.add<int>("aug_blocking", 'p', "Block size for solution phase (128)", false, 128);
    a.add<float>("part_imbalance", 'q', "Imbalance factor for PaToH (3)", false, 3);
    a.add<float>("threshold", 's', "Threshold for CG (1e-12)", false, 0.000000000001);

    a.parse_check(argc, argv);

    std::string A_file = a.get<std::string>("matrix");
    std::string b_file = a.get<std::string>("RHS");
    int zeros = a.get<int>("zeros");
    int nbparts = a.get<int>("nbparts");
    int part_type = a.get<int>("part_type");
    int part_guess = a.get<int>("part_guess");
    int scaling = a.get<int>("scaling");
    int itmax = a.get<int>("itmax");
    int block_size = a.get<int>("block_size");
    int verbose_level = a.get<int>("verbose_level");
    int aug_type = a.get<int>("aug_type");
    int aug_blocking = a.get<int>("aug_blocking");
    float part_imbalance = a.get<float>("part_imbalance");
    float threshold = a.get<float>("threshold");

  int myrank;
  abcd_c *obj;

  int i, j;

  /* Initialize MPI */
  MPI_Init(&argc, &argv);

  /* Find out my identity in the default communicator */
  MPI_Comm_rank(MPI_COMM_WORLD, &myrank);

  obj = new_solver();

  if(myrank == 0) { // the master
    std::string file_A=A_file;
    std::string file_RHS=b_file;

    get_Ab(obj, file_A, file_RHS, zeros);

    obj->icntl[abcd_nbparts] = nbparts;
    obj->icntl[abcd_part_type] = part_type;
    obj->icntl[abcd_part_guess] = part_guess;
    obj->icntl[abcd_scaling] = scaling;
    obj->icntl[abcd_itmax] = itmax;
    obj->icntl[abcd_block_size] = block_size;
    obj->icntl[abcd_verbose_level] = verbose_level;
    obj->icntl[abcd_aug_type] = aug_type;
    obj->icntl[abcd_aug_blocking] = aug_blocking;
    obj->dcntl[abcd_part_imbalance] = part_imbalance;
    obj->dcntl[abcd_threshold] = threshold;
  }
  call_solver(obj, -1);
  call_solver(obj, 6);

  MPI_Finalize();

  return 0;
}

void get_Ab(abcd_c *obj, std::string file_A, std::string file_RHS, int zeros) {
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
        obj->rhs = new double[obj->n];
        for (int i = 0; i < zeros; ++i) 
            obj->rhs[i] = (double) 0;
        for (int i = zeros; i < obj->n - zeros; ++i) {
            obj->rhs[i] = (double) 1;
	}
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
