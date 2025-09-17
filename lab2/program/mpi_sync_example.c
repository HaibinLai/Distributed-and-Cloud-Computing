#include <mpi.h>
#include <stdio.h>
#include <unistd.h>  // lib for sleep

int main(int argc, char **argv) {
  // Initialize the MPI environment. The two arguments to MPI Init are not
  // currently used by MPI implementations, but are there in case future
  // implementations might need the arguments.
  MPI_Init(NULL, NULL);

  // Get the rank of the process
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  int worldSize;
  MPI_Comm_size(MPI_COMM_WORLD, &worldSize);

  // each processes sleeps for as many seconds as its rank
  sleep(world_rank);

  printf("Rank %d enters barrier.\n", world_rank);
  fflush(stdout);

  // blocks until all others have reached this spot
  MPI_Barrier(MPI_COMM_WORLD);

  printf("Hello world from rank %d / %d! \n", world_rank, worldSize);

  // Finalize the MPI environment. No more MPI calls can be made after this
  MPI_Finalize();
}
