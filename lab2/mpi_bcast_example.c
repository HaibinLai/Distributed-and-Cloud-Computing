#include <mpi.h>
#include <stdio.h>

#define ROOT 0

int main(int argc, char** argv) {
  MPI_Init(NULL, NULL);

  // Get the rank of the process
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  int arr_size;

  if (world_rank == 0) {
    // Root process prepares the data to broadcast
    int send_data[] = {100, 200};  // Some value
    arr_size = sizeof(send_data) / sizeof(send_data[0]);

    printf("Process %d broadcasting data: ", world_rank);
    for (int i = 0; i < arr_size; i++) {
      printf("|%d: %d|\t", i, send_data[i]);
    }
    printf("\n");
    fflush(stdout);

    // Broadcast the data from process 0 to all other processes
    MPI_Bcast(&send_data, 2, MPI_INT, 0, MPI_COMM_WORLD);

  } else {
    int rcv_data[2];  // store received data
    // receive broadcasted data
    MPI_Bcast(&rcv_data, 2, MPI_INT, 0, MPI_COMM_WORLD);

    arr_size = sizeof(rcv_data) / sizeof(rcv_data[0]);

    // All processes should now have the same data
    printf("Process %d received following data: ", world_rank);

    for (int i = 0; i < arr_size; i++) {
      printf("|%d: %d|\t", i, rcv_data[i]);
    }
    printf("\n");
  }

  // Finalize the MPI environment. No more MPI calls can be made after this
  MPI_Finalize();
}
