
# MPI 101

## MPI_Comm_rank && MPI_Comm_size

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



## MPI_Send && MPI_Recv

它是一个用 **MPI** 写的最简单的点对点通信示例。




```c
#include <mpi.h>
#include <stdio.h>
```

引入 MPI 的库和标准输入输出。

```c
int main(int argc, char **argv)
{
  MPI_Init(&argc, &argv);
```

* **`MPI_Init`** 初始化 MPI 环境，所有 MPI 程序必须在使用任何 MPI 函数之前调用它。

---

```c
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank); // Get the rank of the process
```

* 获取当前进程的 **rank（编号）**，范围是 `[0, world_size-1]`。
* 这里 `MPI_COMM_WORLD` 表示包含所有进程的通信器。
* `world_rank` = 0 表示进程 0，`world_rank` = 1 表示进程 1。

---

```c
  int sender = 0;
  int receiver = 1;
```

定义角色：`sender` 负责发消息，`receiver` 负责收消息。

---

### 发送端代码（rank = 0 的进程）

```c
  if (world_rank == sender)
  {
    char message[10] = "test"; // Example message
    printf("Process %d sending message \"%s\" to %d\n", world_rank, message, receiver);
    // args:  data    size   type      dest   tag comm_world
    MPI_Send(&message, 10, MPI_CHAR, receiver, 0, MPI_COMM_WORLD);
  }
```

* **发送端进程**（rank = 0）定义一个字符串 `"test"`。
* 调用 `MPI_Send` 把消息发送给 **rank=1** 的进程：

  * `&message`：要发送的数据缓冲区
  * `10`：缓冲区大小（最多传 10 个字符）
  * `MPI_CHAR`：数据类型是字符
  * `receiver`：目标进程（这里是 1）
  * `0`：消息的 tag（标识符，用来区分不同消息）
  * `MPI_COMM_WORLD`：通信器

它会打印一行提示：

```
Process 0 sending message "test" to 1
```

---

### 接收端代码（rank = 1 的进程）

```c
  if (world_rank == receiver)
  {
    char received_message[10];
    MPI_Recv(&received_message, 10, MPI_CHAR, sender, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    printf("Process %d received message \"%s\" from %d \n", world_rank, received_message, sender);
  }
```

* **接收端进程**（rank = 1）准备一个缓冲区接收数据。
* 调用 `MPI_Recv`：

  * `&received_message`：接收缓冲区
  * `10`：缓冲区大小
  * `MPI_CHAR`：数据类型
  * `sender`：消息来源（这里是 0）
  * `0`：tag 必须和发送端匹配
  * `MPI_COMM_WORLD`：通信器
  * `MPI_STATUS_IGNORE`：忽略状态信息

它会打印一行提示：

```
Process 1 received message "test" from 0
```

---

```c
  MPI_Finalize(); // Clean up MPI environment
  return 0;
}
```

* **`MPI_Finalize`**：关闭 MPI 环境，释放资源。
* 所有 MPI 程序在结束前必须调用它。

---

## 实际运行效果

假设用 2 个进程运行：

```bash
mpirun -np 2 ./a.out
```

输出大概是：

```
Process 0 sending message "test" to 1
Process 1 received message "test" from 0
```

---

## 小结

* 进程 0 把 `"test"` 发给进程 1。
* 进程 1 接收到 `"test"` 并打印出来。
* 这是一个 **单向** 的消息传递
---

