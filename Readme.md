
# CS328 — Distributed and Cloud Computing

**By Prof. Georgios Theodoropoulos**
**Student: Haibin Lai (12216112)**

This repository maintains the **slides**, **lab tutorials**, and **assignment materials** for CS328 *Distributed and Cloud Computing*.
The repo is **for study purpose only**（仅用于课程学习）.

---

## 📌 Overview

This course covers fundamental and practical techniques in distributed and cloud computing, including *MPI parallel programming*, *Docker-based distributed execution*, *microservices with gRPC*, *JWT authentication*, *Kafka-based log streaming*, *Spark batch processing*, and *Kubernetes cluster management with Kind*.

The course contains **four major programming assignments**:

| Assignment | Topic                                                    | Main Techniques                                                                         | PDF Source |
| ---------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------- |
| **A1**     | Parallel Matrix Multiplication (OpenMPI + Docker)        | MPI scatter/broadcast/gather, oversubscribed processes, Docker compose testing          |            |
| **A2**     | SUSTech Merch Store (Microservices + gRPC + JWT + Kafka) | REST API, Flask / FastAPI, gRPC services, PostgreSQL DB pool, JWT auth, Kafka streaming |            |
| **A3**     | Distributed Batch Processing using Apache Spark          | PySpark RDD/DataFrame, SQL, window interval operations, time-series analysis            |            |
| **A4**     | Kubernetes Cluster with Kind                             | Deployment, Service, rolling update, scheduling (affinity & taints), load balancing     |            |

---

# 📦 Assignment Summaries


---

## **🟦 Assignment 1 — Parallel Matrix Multiplication (OpenMPI + Docker)**

*PDF: Parallel Matrix Multiplication* 

### ✔ Goals

* Implement parallel **N×N matrix multiplication** using **OpenMPI**
* Use **MPI_Scatter**, **MPI_Bcast**, **MPI_Gather**
* Compare MPI version vs brute-force sequential version
* Test on multiple process counts: **1, 2, 4, 8, 16, 32**
* Test on different matrix sizes: **N = 10, 50, 100, 250, 500**
* Use **Docker Compose** to run the MPI code across **3 containers**

### ✔ Deliverables

* `mpi_matrix.c`, `Dockerfile`, `compose.yaml`
* Timing plots (process count vs latency, size vs latency)
* Report with correctness analysis & screenshots

---

## **🟩 Assignment 2 — SUSTech Merch Store (Microservices + gRPC + JWT + Kafka)**

*PDF: SUSTech Merch Store* 

### ✔ System Architecture

The assignment builds a simplified e-commerce backend consisting of:

* **RESTful API Service** (Flask/FastAPI or Go Gin)
* **gRPC Database Service** with PostgreSQL connection pool
* **gRPC Logging Service** with client-side streaming → Kafka topic
* **JWT-based authentication** for user APIs
* **Docker Compose network** connecting all services

### ✔ Required Features

* Product listing / user registration / login / order placement
* CRUD via DB Service
* Logging via streaming RPC → Kafka
* API specification in **OpenAPI YAML**
* Proto definitions for DB & Logging Service
* Consistent field types across OpenAPI, Proto, database schema

### ✔ Report Questions

Explain implementation steps, JWT auth logic, data type alignment, proto encoding, Kafka pipeline, Docker networking, and testing workflow.

---

## **🟨 Assignment 3 — Distributed Batch Processing using Apache Spark**

*PDF: Apache Spark Batch Processing* 

### ✔ Dataset

Parking utilization dataset (`parking_data_sz.zip`) with columns:
`in_time`, `out_time`, `berthage`, `section`, `admin_region`.

### ✔ Five Required Tasks

1. **Count berthages per section**
2. **List unique berthages per section**
3. **Compute average parking time per section**
4. **Compute average parking time per berthage (sorted)**
5. **Hourly utilization per section**, outputting:

   * `start_time`, `end_time`, `section`, `count`, `percentage`

### ✔ Additional Requirement

* Select **3 sections**, plot **time vs utilization**, and **analyze trends**

### ✔ Notes

* Must use **PySpark API only**
* Can use RDD or DataFrame / Spark SQL
* Output **five CSV files (r1–r5)**

---

## **🟥 Assignment 4 — Exploring Kubernetes with Kind**

*PDF: Kubernetes Assignment* 

### ✔ Task 0 — Deployment & Rolling Update

* Modify Flask API to return: pod name, pod IP, node name
* Add **graceful shutdown** support
* Build image, load into **Kind** cluster (1 control plane + 3 workers)
* Deploy 4 replicas + create a ClusterIP service
* Manually kill a pod → analyze rescheduling
* Add new API `/chat/{username}`
* Perform **rolling update** (maxSurge, maxUnavailable analysis)

### ✔ Task 1 — Pod Scheduling with Affinity & Taints

Cluster: 1 CP + 5 workers, with labels & taints
Requirements:

* **Pod anti-affinity** (replicas must be on different nodes)
* **Preferred weighted node affinity** (powerful > normal > backup)
* Handle node taints (`class=vip`)
* Scale replicas 1→5, analyze scheduling
* Improve configuration if scheduling fails

### ✔ Bonus

Suggest future cloud computing lab ideas
(max +5 points)

---

# 📁 Repository Structure (Recommended)

```
CS328-Distributed-and-Cloud-Computing/
│
├── lec_slides/
├── labs/
│
├── assignment1/
│   ├── mpi_matrix.c
│   ├── Dockerfile
│   ├── compose.yaml
│   └── report.pdf
│
├── assignment2/
│   ├── api_service/
│   ├── db_service/
│   ├── logging_service/
│   ├── docker-compose.yaml
│   └── report.pdf
│
├── assignment3/
│   ├── r1.csv ... r5.csv
│   ├── spark_scripts/
│   └── report.pdf
│
└── assignment4/
    ├── flask_app/
    ├── t0/
    ├── t1/
    └── report.pdf
```

---

# 📌 How to Use This Repo

To build/run different assignments:

### **Assignment 1 (MPI)**

```bash
mpicc mpi_matrix.c -o mpi_matrix
mpirun -np 8 ./mpi_matrix
```

### **Assignment 2 (Microservices)**

```bash
docker compose up --build
```

### **Assignment 3 (Spark)**

Run pyspark from jupyter notebook

### **Assignment 4 (Kubernetes)**

```bash
kind create cluster --config t0/kind-config.yaml
kubectl apply -f t0/t0.yaml
```

---

I would like to express my sincere gratitude to Prof. Georgios Theodoropoulos for designing such a well-structured and inspiring course.
I would also like to thank our TAs for their continuous support — from timely clarifications on Piazza and thoughtful feedback on assignments. Their patience and guidance made the learning experience smooth and highly enjoyable.

Thank you all for your dedication to teaching and for creating a supportive learning environment. This course has been one of the most enriching parts of my semester.