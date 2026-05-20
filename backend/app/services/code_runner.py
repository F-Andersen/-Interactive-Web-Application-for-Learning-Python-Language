import subprocess
import tempfile
import time
from dataclasses import dataclass
import json
from pathlib import Path

from app.core.config import get_settings


@dataclass
class RunResult:
    status: str
    stdout: str
    stderr: str
    execution_time_ms: int


class DockerCodeRunner:
    def run(self, code: str, input_data: str | None, timeout_ms: int, memory_limit_mb: int) -> RunResult:
        settings = get_settings()
        timeout_seconds = max(timeout_ms / 1000, 1)
        runner_script = (
            "import json, subprocess, sys; "
            "payload=json.load(sys.stdin); "
            "open('/tmp/solution.py','w',encoding='utf-8').write(payload['code']); "
            "p=subprocess.run(['python','/tmp/solution.py'],input=payload.get('stdin',''),text=True,capture_output=True); "
            "sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); sys.exit(p.returncode)"
        )
        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            settings.runner_network,
            "--memory",
            f"{memory_limit_mb}m",
            "--cpus",
            "1",
            "-i",
            settings.runner_image,
            "python",
            "-c",
            runner_script,
        ]
        start = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                input=json.dumps({"code": code, "stdin": input_data or ""}),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = int((time.perf_counter() - start) * 1000)
            return RunResult("time_limit", exc.stdout or "", exc.stderr or "Time limit exceeded", elapsed)
        elapsed = int((time.perf_counter() - start) * 1000)
        if completed.returncode != 0:
            stderr = completed.stderr or ""
            status = "compile_error" if "SyntaxError" in stderr else "runtime_error"
            return RunResult(status, completed.stdout, stderr, elapsed)
        return RunResult("accepted", completed.stdout, completed.stderr, elapsed)


class LocalCodeRunner:
    """Used by tests only; production uses DockerCodeRunner."""

    def run(self, code: str, input_data: str | None, timeout_ms: int, memory_limit_mb: int) -> RunResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            code_path = Path(temp_dir) / "solution.py"
            code_path.write_text(code, encoding="utf-8")
            start = time.perf_counter()
            try:
                completed = subprocess.run(
                    ["python", str(code_path)],
                    input=input_data or "",
                    capture_output=True,
                    text=True,
                    timeout=max(timeout_ms / 1000, 1),
                )
            except subprocess.TimeoutExpired:
                elapsed = int((time.perf_counter() - start) * 1000)
                return RunResult("time_limit", "", "Time limit exceeded", elapsed)
            elapsed = int((time.perf_counter() - start) * 1000)
            if completed.returncode != 0:
                status = "compile_error" if "SyntaxError" in completed.stderr else "runtime_error"
                return RunResult(status, completed.stdout, completed.stderr, elapsed)
            return RunResult("accepted", completed.stdout, completed.stderr, elapsed)
