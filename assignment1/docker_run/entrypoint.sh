#!/usr/bin/env bash
set -euo pipefail

user=mpi
home=/home/$user

# 必须用 root 起：sshd 要写 /etc/ssh/ssh_host_* 和监听 22
if [ "$(id -u)" != "0" ]; then
  echo "This entrypoint must run as root."
  exit 1
fi

# 1) 生成并确保系统 host keys 存在（关键修复点）
mkdir -p /etc/ssh
ssh-keygen -A

# 2) 准备用户与共享 SSH 密钥（容器间免密）
mkdir -p "$home/.ssh" /var/run/sshd /workspace/ssh
chmod 700 "$home/.ssh"

if [ ! -f /workspace/ssh/id_rsa ]; then
  ssh-keygen -t rsa -b 4096 -N "" -f /workspace/ssh/id_rsa
fi
cp /workspace/ssh/id_rsa{,.pub} "$home/.ssh/"
cat /workspace/ssh/id_rsa.pub >> "$home/.ssh/authorized_keys"

cat > "$home/.ssh/config" <<EOF
Host *
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  LogLevel ERROR
EOF

chown -R $user:$user "$home/.ssh"
chmod 600 "$home/.ssh"/*

# 3) 启动 sshd（守护进程方式）
/usr/sbin/sshd

# 4) 保持容器常驻（切到 mpi 用户）
exec su - $user -c "cd /workspace && tail -f /dev/null"
