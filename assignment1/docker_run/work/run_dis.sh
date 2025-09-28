#!/bin/bash

mpicc mpi_matrix_base.c -o matmul

prog=./matmul

# number of processes to test
procs=(1 2 4 8 16 32)

for p in "${procs[@]}"; do
    echo "Running with $p processes..."
    mpirun -np $p $prog
    echo ""
done
