# from flask import Flask
# import os

# app = Flask(__name__)


# @app.route('/')
# def hello():
#   server_name = os.getenv('SERVER_NAME', 'Unknown Server')
#   return f'Hello from {server_name}!'


# if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)))

from flask import Flask
import os
import socket
import signal
import sys

app = Flask(__name__)

# ---- Graceful Shutdown ----
def handle_sigterm(signum, frame):
    print("Received SIGTERM, shutting down gracefully...")
    # 这里可以加一些 cleanup，如果有的话
    sys.exit(0)

# 监听 SIGTERM（K8s 删除 Pod 时会发）
signal.signal(signal.SIGTERM, handle_sigterm)


@app.route("/")
def hello():
    # 从环境变量/系统中拿信息
    pod_name = os.getenv("POD_NAME", socket.gethostname())
    node_name = os.getenv("NODE_NAME", "unknown-node")

    # Pod IP：用 hostname 解析通常等于 pod IP
    try:
        pod_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        pod_ip = "unknown-ip"

    return (
        f"Hello from pod={pod_name}, "
        f"ip={pod_ip}, "
        f"node={node_name}!\n"
    )


# 新增的 greet-with-info API
@app.route("/chat/<username>")
def chat(username):
    pod_name = os.getenv("POD_NAME", socket.gethostname())
    node_name = os.getenv("NODE_NAME", "unknown-node")

    return (
        f"Hello {username}! "
        f"This response is served by pod={pod_name} on node={node_name}.\n"
    )


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
