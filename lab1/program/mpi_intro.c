#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv)
{
  // Initialize the MPI environment. The two arguments to MPI Init are not
  // currently used by MPI implementations, but are there in case future
  // implementations might need the arguments.
  MPI_Init(NULL, NULL);


/*
这两个函数是 MPI（Message Passing Interface）里最基础的接口，用来获取进程在通信器（comm）里的信息：

1. **`MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);`**

   * `MPI_COMM_WORLD` 是一个默认的通信器，表示所有参与运行这个 MPI 程序的进程。
   * `MPI_Comm_rank` 会告诉你 **当前进程在这个通信器里的编号**（叫做 *rank*）。
   * Rank 从 0 开始编号，一直到 `world_size-1`。
   * 所以 `world_rank` 表示“我是第几个进程”。

   👉 举例：假设一共启动了 4 个进程，那么 rank 就是 `0,1,2,3`。每个进程调用这个函数时，会得到自己独一无二的 rank。

---

2. **`MPI_Comm_size(MPI_COMM_WORLD, &world_size);`**

   * 这个函数返回通信器里总共有多少个进程。
   * 对于 `MPI_COMM_WORLD`，它就是你运行程序时 `mpirun -np X` 指定的进程数 X。
   * 所以 `world_size` 表示“进程总数”。

---

✨ 结合起来用：

```c
printf("Hello from rank %d out of %d processes\n", world_rank, world_size);
```

如果你用 `mpirun -np 4 ./a.out` 启动程序，输出可能是：

```
Hello from rank 0 out of 4 processes
Hello from rank 1 out of 4 processes
Hello from rank 2 out of 4 processes
Hello from rank 3 out of 4 processes
```

---

要不要我帮你画个图，直观展示 rank 和 size 的关系？

*/
  // Get the number of processes
  int world_size;
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);

  // Get the rank of the process
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  // Get the name of the processor
  char processor_name[MPI_MAX_PROCESSOR_NAME];
  int name_len;
  MPI_Get_processor_name(processor_name, &name_len);

  // Print off a hello world message
  printf("Hello world from processor %s, rank %d out of %d processors \n", processor_name, world_rank, world_size);

  // Finalize the MPI environment. No more MPI calls can be made after this
  MPI_Finalize();
}
