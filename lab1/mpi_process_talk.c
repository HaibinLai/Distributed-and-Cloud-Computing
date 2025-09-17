#include <mpi.h>
#include <stdio.h>

// TASK: Create 2 mpi processes that implement the ping pong programm.
// Ping Pong: When you receive a "ping" message you respond with "pong" and vice versa

int main(int argc, char **argv)
{
  MPI_Init(&argc, &argv);
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank); // Get the rank of the process

  int sender = 0;
  int receiver = 1;

  if (world_rank == sender)
  {
    char message[10] = "test"; // Example message
    printf("Process %d sending message \"%s\" to %d\n", world_rank, message, receiver);
    // args:  data    size   type      dest   tag comm_world
    MPI_Send(&message, 10, MPI_CHAR, receiver, 0, MPI_COMM_WORLD);
  }

  if (world_rank == receiver)
  {
    // Process 5 receives the message from Process 1
    char received_message[10];
    // args:     data_buff      size   type    src      tag  comm_world      status
    MPI_Recv(&received_message, 10, MPI_CHAR, sender, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    printf("Process %d received message \"%s\" from %d \n", world_rank, received_message, sender);
  }

  MPI_Finalize(); // Clean up MPI environment

  return 0;
}