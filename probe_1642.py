"""PROBE for btclib-org/.github#1642, not to land.

Prints yes/no and counts only, never a value read.
Arguments: <label> <runner home> <workspace> <tmp marker> [--spawn]
"""

import os
import re
import socket
import subprocess
import sys

label, home, workspace, marker = sys.argv[1:5]
TOKEN = re.compile(
    rb"gh[pousr]_[A-Za-z0-9]{30,}|sk-ant-[A-Za-z0-9_-]{20,}"
    rb"|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}"
)


def out(key, value):
    print(f"PROBE {label} {key}={value}", flush=True)


def yn(f):
    try:
        f()
    except Exception:
        return "no"
    return "yes"


def conn(host, port):
    socket.create_connection((host, port), timeout=5).close()


def loop():
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    socket.create_connection(srv.getsockname(), timeout=5).close()
    srv.close()


out("uid_is_root", "yes" if os.getuid() == 0 else "no")
out("resolve_github", yn(lambda: socket.getaddrinfo("github.com", 443)))
out("resolve_localhost", yn(lambda: socket.getaddrinfo("localhost", 80)))
out("connect_ip_1.1.1.1_443", yn(lambda: conn("1.1.1.1", 443)))
out("connect_ip6_cloudflare_443", yn(lambda: conn("2606:4700:4700::1111", 443)))
out("connect_imds_169.254.169.254_80", yn(lambda: conn("169.254.169.254", 80)))
out("connect_stub_127.0.0.53_53", yn(lambda: conn("127.0.0.53", 53)))
out("loopback_listen_connect", yn(loop))
for path in (
    "/run/systemd/resolve/io.systemd.Resolve",
    "/var/run/docker.sock",
    home,
    workspace,
    marker,
):
    out(f"exists[{path}]", "yes" if os.path.exists(path) else "no")
out("home_entries", len(os.listdir("/home")))
pids = [p for p in os.listdir("/proc") if p.isdigit()]
out("pids_visible", len(pids))
others = 0
for p in pids:
    try:
        others += os.stat(f"/proc/{p}").st_uid != os.getuid()
    except OSError:
        pass
out("pids_of_other_uids", others)
hits = 0
for p in pids:
    for f in ("environ", "cmdline"):
        try:
            with open(f"/proc/{p}/{f}", "rb") as fh:
                hits += bool(TOKEN.search(fh.read()))
        except OSError:
            pass
out("token_shapes_in_proc", hits)
SKIP = {".venv", ".git", "python", "cache", ".cache", ".rustup", ".cargo",
        ".dotnet", "_tool", "_actions", ".nvm", ".npm", "bitcoin", "node_modules"}
files = 0
for top in (home, "/tmp", "/var/tmp", "/dev/shm", "/var/lib/review-pr"):
    for root, dirs, names in os.walk(top):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for n in names:
            try:
                path = os.path.join(root, n)
                if os.path.getsize(path) < 2_000_000:
                    with open(path, "rb") as fh:
                        if TOKEN.search(fh.read()):
                            files += 1
                            out("token_shape_file", path)
            except OSError:
                pass
out("token_shapes_in_files", files)
out("env_names", ",".join(sorted(os.environ)))
out(
    "sudo",
    yn(lambda: subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)),
)
status = dict(
    line.split(":", 1) for line in open("/proc/self/status") if ":" in line
)
out("NoNewPrivs", status["NoNewPrivs"].strip())
out("CapEff_zero", "yes" if int(status["CapEff"].strip(), 16) == 0 else "no")
with open(f"/tmp/probe-written-{label}", "w") as fh:
    fh.write("x")
if "--spawn" in sys.argv:
    subprocess.Popen(
        ["sleep", "600"], start_new_session=True,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    out("spawned_detached_sleep", "yes")
