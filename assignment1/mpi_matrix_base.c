#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define MAT_SIZE 500

void brute_force_matmul(double mat1[MAT_SIZE][MAT_SIZE], double mat2[MAT_SIZE][MAT_SIZE], 
                        double res[MAT_SIZE][MAT_SIZE]) {
   /* matrix multiplication of mat1 and mat2, store the result in res */
    for (int i = 0; i < MAT_SIZE; ++i) {
        for (int j = 0; j < MAT_SIZE; ++j) {
            res[i][j] = 0;
            for (int k = 0; k < MAT_SIZE; ++k) {
                res[i][j] += mat1[i][k] * mat2[k][j];
            }
        }
    }
}

int checkRes(const double target[MAT_SIZE][MAT_SIZE], const double res[MAT_SIZE][MAT_SIZE]) {
   /* check whether the obtained result is the same as the intended target; if true return 1, else return 0 */
   for (int i = 0; i < MAT_SIZE; ++i) {
      for (int j = 0; j < MAT_SIZE; ++j) {
         if (res[i][j] != target[i][j]) {
            return 0;
         }
      }
   }
   return 1;
}

int main(int argc, char *argv[])
{
   int rank, mpiSize;
   double a[MAT_SIZE][MAT_SIZE],      /* matrix A to be multiplied */
         b[MAT_SIZE][MAT_SIZE],       /* matrix B to be multiplied */
         c[MAT_SIZE][MAT_SIZE],       /* result matrix C */
         bfRes[MAT_SIZE][MAT_SIZE];   /* brute force result bfRes */

   /* You need to intialize MPI here */
   MPI_Init(&argc, &argv);
   MPI_Comm_rank(MPI_COMM_WORLD, &rank);
   MPI_Comm_size(MPI_COMM_WORLD, &mpiSize);

   int *sendcounts = malloc(mpiSize * sizeof(int));
   int *displs     = malloc(mpiSize * sizeof(int));

   int myrows = 0; // rows of matrix A assigned to each process

   /* root */
   if (rank == 0) {
      /* First, fill some numbers into the matrix */
      for (int i = 0; i < MAT_SIZE; i++) {
         for (int j = 0; j < MAT_SIZE; j++) {
                a[i][j] = i + j;
                b[i][j] = i * j;
                c[i][j] = 0.0;
         }
      }

      double start = MPI_Wtime();
   
      /* Send matrix data to the worker tasks */
      MPI_Bcast(&b[0][0], MAT_SIZE*MAT_SIZE, MPI_DOUBLE, 0, MPI_COMM_WORLD);

      // split A by row
      int rows_per_proc = MAT_SIZE / mpiSize;
      int rem = MAT_SIZE % mpiSize;
      int offset = 0;
      for (int p = 0; p < mpiSize; p++) {
         int rows = rows_per_proc + (p < rem ? 1 : 0);
         sendcounts[p] = rows * MAT_SIZE;     // number of elements
         displs[p]     = offset * MAT_SIZE;   // displacement (in elements)
         offset += rows;
      }
      myrows = sendcounts[rank] / MAT_SIZE;

      // each process's local buffer
      double *A_local = malloc((size_t)myrows * MAT_SIZE * sizeof(double));
      double *C_local = calloc((size_t)myrows * MAT_SIZE, sizeof(double));

      // distribute rows of A
      MPI_Scatterv(&a[0][0], sendcounts, displs, MPI_DOUBLE,
         A_local, myrows*MAT_SIZE, MPI_DOUBLE,
         0, MPI_COMM_WORLD);

      /* Compute its own piece */
      for (int i = 0; i < myrows; i++) {
         for (int k = 0; k < MAT_SIZE; k++) {
               double a_k = A_local[i*MAT_SIZE + k];
               for (int j = 0; j < MAT_SIZE; j++) {
                  C_local[i*MAT_SIZE + j] += a_k * b[k][j];
               }
         }
      }

      MPI_Barrier(MPI_COMM_WORLD);

      /* Receive results from worker tasks */
      MPI_Gatherv(C_local, myrows*MAT_SIZE, MPI_DOUBLE,
                &c[0][0], sendcounts, displs, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

      free(A_local);
      free(C_local);

      MPI_Barrier(MPI_COMM_WORLD);

      /* Measure finish time */
      double finish = MPI_Wtime();
      
      printf("Done in %f seconds.\n", finish - start);

      /* Compare results with those from brute force */
      // start = MPI_Wtime();

      brute_force_matmul(a, b, bfRes);

      // finish = MPI_Wtime();
      // printf("Brute force done in %f seconds.\n", finish - start);

      if (!checkRes(bfRes, c)) {
         printf("ERROR: mismatch!\n");
      } else {
         printf("Result is correct.\n");
      }

   }else{
      /* worker */
      /* Receive data from root and compute, then send back to root */
      MPI_Bcast(&b[0][0], MAT_SIZE*MAT_SIZE, MPI_DOUBLE, 0, MPI_COMM_WORLD);
      // spilt A by row
      int rows_per_proc = MAT_SIZE / mpiSize;
      int rem = MAT_SIZE % mpiSize;
      int offset = 0;
      for (int p = 0; p < mpiSize; p++) {
         int rows = rows_per_proc + (p < rem ? 1 : 0);
         sendcounts[p] = rows * MAT_SIZE;     // number of elements
         displs[p]     = offset * MAT_SIZE;   // displacement (in elements)
         offset += rows;
      }
      myrows = sendcounts[rank] / MAT_SIZE;

      // each process's local buffer
      double *A_local = malloc((size_t)myrows * MAT_SIZE * sizeof(double));
      double *C_local = calloc((size_t)myrows * MAT_SIZE, sizeof(double));

      // distribute rows of A
      MPI_Scatterv(&a[0][0], sendcounts, displs, MPI_DOUBLE,
         A_local, myrows*MAT_SIZE, MPI_DOUBLE,
         0, MPI_COMM_WORLD);
      
      /* Compute its own piece */
      for (int i = 0; i < myrows; i++) {
         for (int k = 0; k < MAT_SIZE; k++) {
            double aik = A_local[i*MAT_SIZE + k];
            for (int j = 0; j < MAT_SIZE; j++) {
               C_local[i*MAT_SIZE + j] += aik * b[k][j];
            }
         }
      }

      MPI_Barrier(MPI_COMM_WORLD);

      MPI_Gatherv(C_local, myrows*MAT_SIZE, MPI_DOUBLE,
         &c[0][0], sendcounts, displs, MPI_DOUBLE,
         0, MPI_COMM_WORLD);

      free(A_local);
      free(C_local);

      MPI_Barrier(MPI_COMM_WORLD);
   }

   free(sendcounts);
   free(displs);

   /* Don't forget to finalize your MPI application */
   MPI_Finalize();
   return 0;
}