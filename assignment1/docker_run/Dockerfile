FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential openmpi-bin libopenmpi-dev \
      openssh-server openssh-client ca-certificates sudo && \
    rm -rf /var/lib/apt/lists/*

# 创建用户（避免用 root 跑 MPI）
RUN useradd -ms /bin/bash mpi && echo "mpi ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# SSH 基础设置
RUN mkdir -p /var/run/sshd
# 允许无交互连接（我们用已知密钥；禁掉密码登录更安全）
RUN sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config

WORKDIR /workspace
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R mpi:mpi /workspace

# USER mpi
ENTRYPOINT ["bash", "/entrypoint.sh"]
# ENTRYPOINT ["/entrypoint.sh"]
