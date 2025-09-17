#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  // lib for sleep

int main(int argc, char** argv) {
  MPI_Init(&argc, &argv);

  int world_size, world_rank;
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  int root = 0;

  // how many data to pass to each worker
  int data_per_worker;
  if (argc > 1) {
    data_per_worker = atoi(argv[1]);
  } else {
    data_per_worker = 5;
  }

  // how many data to generate in total
  int total_data = world_size * data_per_worker;

  // send receive buffers
  int sendbuf[total_data];
  int recvbuf[data_per_worker];

  // Initialize the data on the root process
  if (world_rank == root) {
    for (int i = 0; i < total_data; i++) {
      sendbuf[i] = i;
    }
  }

  // Scatter the data from the root process to all processes
  MPI_Scatter(sendbuf, data_per_worker, MPI_INT, recvbuf, data_per_worker,
              MPI_INT, root, MPI_COMM_WORLD);

  // Print the received data on each process
  printf("Process %d received data: ", world_rank);
  for (int i = 0; i < data_per_worker; i++) {
    printf("%d ", recvbuf[i]);
  }
  printf("\n");

  printf("Process %d starting processing data...\n", world_rank);

  for (int i = 0; i < data_per_worker; i++) {
    recvbuf[i] += 100 * world_rank;
  }

  printf("Process %d finished with work! \n", world_rank);

  // each processes sends processes data back to root (including root!!)
  MPI_Gather(recvbuf, data_per_worker, MPI_INT, sendbuf, data_per_worker,
             MPI_INT, root, MPI_COMM_WORLD);

  // root prints gather list
  if (world_rank == root) {
    sleep(1);
    printf("Root (Process 0) gathered the following list from the workers: ");
    for (int i = 0; i < total_data; i++) {
      printf("%d ", sendbuf[i]);
    }
    printf("\n");
  }

  MPI_Finalize();
  return 0;
}
