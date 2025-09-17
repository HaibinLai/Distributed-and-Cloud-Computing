#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
  MPI_Init(NULL, NULL);

  int worldRank;
  MPI_Comm_rank(MPI_COMM_WORLD, &worldRank);

  int results[4];
  int res;

  if (worldRank == 0) {
    int send_data[] = {200, 100};
    MPI_Bcast(&send_data, 2, MPI_INT, 0, MPI_COMM_WORLD);

    res = send_data[0] + send_data[1];
  } else {
    int rcv_data[2];
    MPI_Bcast(&rcv_data, 2, MPI_INT, 0, MPI_COMM_WORLD);

    if (worldRank == 1) {
      res = rcv_data[0] - rcv_data[1];
    } else if (worldRank == 2) {
      res = rcv_data[0] * rcv_data[1];
    } else if (worldRank == 3) {
      res = rcv_data[0] / rcv_data[1];
    }
  }

  MPI_Gather(&res, 1, MPI_INT, &results, 1, MPI_INT, 0, MPI_COMM_WORLD);

  if (worldRank == 0) {
    printf("add: %d, minus: %d, mult: %d, div: %d\n", results[0], results[1],
           results[2], results[3]);
  }

  MPI_Finalize();
}
