#!/usr/bin/env python3
import subprocess
import re
from collections import defaultdict

import matplotlib.pyplot as plt


# ====== 配置区 ======
URL = "http://localhost:8080/products"  # 你的接口
TOTAL_REQUESTS = 2000                   # hey -n
CONCURRENCIES = [50, 100, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]  # hey -c 列表
# ====================


def run_hey(concurrency: int):
    """
    Run `hey` with given concurrency and return its stdout as string.
    """
    cmd = [
        "hey",
        "-n", str(TOTAL_REQUESTS),
        "-c", str(concurrency),
        URL,
    ]
    print(f"\n=== Running: {' '.join(cmd)} ===")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        print(f"[WARN] hey failed with return code {proc.returncode}")
        print("stderr:")
        print(proc.stderr)
        # 仍然返回 stdout，尽量解析
    return proc.stdout


def parse_hey_output(output: str):
    """
    Parse hey output:
      - Requests/sec
      - Status code distribution
    Return dict with keys:
      'requests_per_sec': float
      'status_codes': dict[int, int]
    """
    result = {
        "requests_per_sec": None,
        "status_codes": defaultdict(int),
    }

    # 1) Requests/sec
    m = re.search(r"Requests/sec:\s+([0-9.]+)", output)
    if m:
        result["requests_per_sec"] = float(m.group(1))

    # 2) Status code distribution section
    #    找到 "Status code distribution:" 这一行的下标
    lines = output.splitlines()
    try:
        idx = next(i for i, line in enumerate(lines) if "Status code distribution:" in line)
    except StopIteration:
        # 没找到就算了
        return result

    # 从下一行开始，直到遇到空行或者非状态码行
    status_code_pattern = re.compile(r"\[(\d+)\]\s+(\d+)\s+responses")
    for line in lines[idx + 1:]:
        line = line.strip()
        if not line:
            break
        m = status_code_pattern.search(line)
        if not m:
            # 不是 [xxx] n responses 的行就停
            break
        code = int(m.group(1))
        count = int(m.group(2))
        result["status_codes"][code] += count

    return result


def is_success_status(code: int) -> bool:
    """
    定义“成功”的状态码范围。
    这里简单设定为 2xx 都算成功。
    如果只想看 200，也可以改成 `return code == 200`。
    """
    return 200 <= code < 300


def main():
    all_results = []

    for c in CONCURRENCIES:
        out = run_hey(c)
        parsed = parse_hey_output(out)
        status_codes = parsed["status_codes"]
        rps = parsed["requests_per_sec"]

        total = sum(status_codes.values())
        success = sum(cnt for code, cnt in status_codes.items() if is_success_status(code))
        success_rate = (success / TOTAL_REQUESTS) * 100 if total > 0 else 0.0

        all_results.append({
            "concurrency": c,
            "rps": rps,
            "status_codes": dict(status_codes),
            "total": total,
            "success": success,
            "success_rate": success_rate,
        })

        # 打印一份表格到终端
        print(f"\n--- Concurrency = {c} ---")
        print(f"Requests/sec: {rps}")
        print("Status codes:")
        for code, cnt in sorted(status_codes.items()):
            print(f"  {code}: {cnt}")
        print(f"Total: {total}, Success(2xx): {success}, Success rate: {success_rate:.2f}%")

    # 画图
    conc_list = [r["concurrency"] for r in all_results]
    rps_list = [r["rps"] for r in all_results]
    succ_rate_list = [r["success_rate"] for r in all_results]

    plt.figure(figsize=(10, 8))

    # 子图1: Requests/sec vs concurrency
    plt.subplot(2, 1, 1)
    plt.plot(conc_list, rps_list, marker="o")
    plt.title("Hey Benchmark Results")
    plt.ylabel("Requests/sec")
    plt.grid(True, linestyle="--", alpha=0.5)

    # 子图2: Success rate vs concurrency
    plt.subplot(2, 1, 2)
    plt.plot(conc_list, succ_rate_list, marker="s")
    plt.xlabel("Concurrency (-c)")
    plt.ylabel("Success rate (%)")
    plt.ylim(0, 105)
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("hey_benchmark.png", dpi=200, bbox_inches="tight")
    plt.show()

    print("\nSaved figure to hey_benchmark.png")


if __name__ == "__main__":
    main()
