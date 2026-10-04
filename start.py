from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
FRONTEND_DIR = ROOT / "frontend"
REQUIREMENTS = ROOT / "requirements.txt"
INSTALL_STATE_DIR = ROOT / ".simulator_state"
PYTHON_REQ_MARKER = INSTALL_STATE_DIR / "requirements.sha256"
FRONTEND_REQ_MARKER = INSTALL_STATE_DIR / "frontend.sha256"


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_checked(command: list[str], cwd: Path = ROOT) -> None:
    print(f"\n[SETUP] {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def _ensure_python_environment() -> Path:
    venv_python = _venv_python()
    if not venv_python.exists():
        print("[SETUP] Creating isolated Python environment (.venv)...")
        _run_checked([sys.executable, "-m", "venv", str(VENV_DIR)])

    INSTALL_STATE_DIR.mkdir(exist_ok=True)
    current_hash = _hash_file(REQUIREMENTS)
    installed_hash = PYTHON_REQ_MARKER.read_text().strip() if PYTHON_REQ_MARKER.exists() else ""

    if current_hash != installed_hash:
        print("[SETUP] Installing/updating Python dependencies...")
        try:
            _run_checked([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                "\n[ERROR] Python dependency installation failed. Check your internet connection, "
                "then run 'python start.py' again."
            ) from exc
        PYTHON_REQ_MARKER.write_text(current_hash)
    else:
        print("[SETUP] Python dependencies already ready.")

    return venv_python


def _npm_command(npm: str, *args: str) -> list[str]:
    """Return an npm command that is safe when Node is under Program Files.

    On Windows, npm is normally a .cmd shim. Passing that shim through
    ``cmd.exe /c`` as separate argv items breaks when its path contains spaces
    (for example ``C:\\Program Files\\nodejs\\npm.cmd``). Instead we call
    npm's JavaScript CLI directly with node.exe whenever possible.
    """
    if os.name == "nt" and Path(npm).suffix.lower() in {".cmd", ".bat"}:
        node = shutil.which("node") or shutil.which("node.exe")
        if node:
            npm_cli = Path(node).resolve().parent / "node_modules" / "npm" / "bin" / "npm-cli.js"
            if npm_cli.exists():
                return [node, str(npm_cli), *args]

        # Fallback for unusual Node installations. Supplying the whole command
        # after /c as a single string preserves quoting around paths with spaces.
        command_line = subprocess.list2cmdline([npm, *args])
        return [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", command_line]

    return [npm, *args]


def _find_npm() -> str:
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    node = shutil.which("node") or shutil.which("node.exe")
    if not npm or not node:
        print(
            "\n[ERROR] Node.js/npm is not installed or is not available in PATH.\n"
            "Install the current Node.js LTS release, close VS Code completely, reopen it,\n"
            "and run this command again.\n"
        )
        raise SystemExit(2)

    try:
        version_text = subprocess.check_output([node, "--version"], text=True).strip().lstrip("v")
        major, minor, *_ = (int(part) for part in version_text.split("."))
        if major < 20 or (major == 20 and minor < 19):
            raise ValueError
    except (subprocess.SubprocessError, ValueError):
        print(
            "\n[ERROR] This frontend requires Node.js 20.19+ (or a newer LTS release).\n"
            "Update Node.js, restart VS Code, then run 'python start.py' again.\n"
        )
        raise SystemExit(2)
    return npm


def _ensure_frontend_environment(npm: str) -> None:
    package_json = FRONTEND_DIR / "package.json"
    lock_file = FRONTEND_DIR / "package-lock.json"
    node_modules = FRONTEND_DIR / "node_modules"

    if not package_json.exists():
        raise SystemExit("[ERROR] frontend/package.json is missing.")

    digest = hashlib.sha256(package_json.read_bytes())
    if lock_file.exists():
        digest.update(lock_file.read_bytes())
    current_hash = digest.hexdigest()
    installed_hash = FRONTEND_REQ_MARKER.read_text().strip() if FRONTEND_REQ_MARKER.exists() else ""

    if not node_modules.exists() or current_hash != installed_hash:
        print("[SETUP] Installing/updating frontend dependencies...")
        command = _npm_command(npm, "ci") if lock_file.exists() else _npm_command(npm, "install")
        try:
            _run_checked(command, cwd=FRONTEND_DIR)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                "\n[ERROR] Frontend dependency installation failed. Check your internet connection "
                "and Node.js installation, then run 'python start.py' again."
            ) from exc
        FRONTEND_REQ_MARKER.write_text(current_hash)
    else:
        print("[SETUP] Frontend dependencies already ready.")


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _stream_output(process: subprocess.Popen[str], label: str) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        print(f"[{label}] {line.rstrip()}")


def _wait_for_url(url: str, timeout_seconds: float = 45.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def _start_processes(venv_python: Path, npm: str, backend_port: int, frontend_port: int) -> tuple[subprocess.Popen[str], subprocess.Popen[str]]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(ROOT))
    env.setdefault("VITE_API_URL", f"http://localhost:{backend_port}")

    backend_cmd = [
        str(venv_python),
        "-m",
        "uvicorn",
        "backend.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        str(backend_port),
    ]
    frontend_cmd = _npm_command(npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", str(frontend_port), "--strictPort")

    common = dict(cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    backend = subprocess.Popen(backend_cmd, **common)
    frontend = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    threading.Thread(target=_stream_output, args=(backend, "BACKEND"), daemon=True).start()
    threading.Thread(target=_stream_output, args=(frontend, "FRONTEND"), daemon=True).start()
    return backend, frontend


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="One-command launcher for the Cricket Decision Review Simulator")
    parser.add_argument("--setup-only", action="store_true", help="Install dependencies, then exit")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--frontend-port", type=int, default=5173)
    args = parser.parse_args()

    print("=" * 72)
    print(" CRICKET DECISION REVIEW SIMULATOR — ONE TERMINAL LAUNCHER")
    print("=" * 72)

    if sys.version_info < (3, 11):
        # Windows commonly keeps an older Python as the default while a newer
        # version is available through the py launcher. Re-launch automatically
        # so the user can still run simply: python start.py
        if os.name == "nt":
            py_launcher = shutil.which("py") or shutil.which("py.exe")
            if py_launcher:
                print(
                    f"[SETUP] Default Python is {sys.version_info.major}.{sys.version_info.minor}. "
                    "Trying installed Python 3.11..."
                )
                try:
                    return subprocess.call([py_launcher, "-3.11", str(Path(__file__).resolve()), *sys.argv[1:]])
                except OSError:
                    pass
        print("[ERROR] Python 3.11 or newer is required.")
        print("Run with: py -3.11 start.py")
        return 2

    npm = _find_npm()
    venv_python = _ensure_python_environment()
    _ensure_frontend_environment(npm)

    if args.setup_only:
        print("\n[READY] Setup complete. Next time run: python start.py")
        return 0

    if not _port_available(args.backend_port):
        print(f"[ERROR] Port {args.backend_port} is already in use. Close the old backend or use --backend-port.")
        return 3
    if not _port_available(args.frontend_port):
        print(f"[ERROR] Port {args.frontend_port} is already in use. Close the old frontend or use --frontend-port.")
        return 3

    print("\n[START] Launching backend and frontend in this terminal...")
    backend, frontend = _start_processes(venv_python, npm, args.backend_port, args.frontend_port)

    frontend_url = f"http://localhost:{args.frontend_port}"
    backend_url = f"http://localhost:{args.backend_port}"

    try:
        backend_ready = _wait_for_url(f"{backend_url}/system/status", timeout_seconds=45)
        frontend_ready = _wait_for_url(frontend_url, timeout_seconds=45)

        if backend_ready and frontend_ready:
            print("\n" + "=" * 72)
            print(" SIMULATOR READY")
            print(f" Frontend : {frontend_url}")
            print(f" API docs : {backend_url}/docs")
            print(" Stop both services with Ctrl+C")
            print("=" * 72 + "\n")
            if not args.no_browser:
                webbrowser.open(frontend_url)
        else:
            print("\n[WARNING] One or both services did not become ready within the startup window.")
            print("Check the BACKEND and FRONTEND log lines above for the cause.")

        while True:
            if backend.poll() is not None:
                print("\n[ERROR] Backend stopped unexpectedly.")
                return backend.returncode or 1
            if frontend.poll() is not None:
                print("\n[ERROR] Frontend stopped unexpectedly.")
                return frontend.returncode or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down simulator...")
        return 0
    finally:
        _terminate(frontend)
        _terminate(backend)
        print("[STOP] Backend and frontend stopped.")


if __name__ == "__main__":
    raise SystemExit(main())
