from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRATCH = REPO / "docs" / "ai_agents" / "local" / ".tmp" / "rerevved-ghidra"


def ghidra_classpath() -> str | None:
    root = os.environ.get("REREVVED_GHIDRA_HOME")
    if not root:
        return None
    jars = sorted(Path(root).rglob("*.jar"))
    return os.pathsep.join(str(path) for path in jars) if jars else None


def matching_brace(source: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise AssertionError("unmatched brace")


def java_method(source: str, signature: str) -> str:
    start = source.index(signature)
    return source[start : matching_brace(source, source.index("{", start))]


class JavaFixture:
    def __init__(self, owner, sources: dict[str, str], production=(), classpath=""):
        javac = shutil.which("javac")
        self.java = shutil.which("java")
        if javac is None or self.java is None:
            raise AssertionError("JDK java and javac are required for lifecycle proof")
        SCRATCH.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="java-fixture-", dir=SCRATCH)
        self.root = Path(temporary.name)

        def cleanup():
            if self.root.resolve().parent != SCRATCH.resolve():
                raise AssertionError(
                    "refusing to remove fixture outside Ghidra scratch"
                )
            temporary.cleanup()

        register_cleanup = (
            owner.addClassCleanup if isinstance(owner, type) else owner.addCleanup
        )
        register_cleanup(cleanup)
        paths = []
        for name, text in sources.items():
            path = self.root / name
            path.write_text(text, encoding="utf-8")
            paths.append(str(path))
        classes = self.root / "classes"
        classes.mkdir()
        self.classpath = os.pathsep.join(filter(None, (str(classes), classpath)))
        command = [javac, "-proc:none", "-encoding", "UTF-8", "-d", str(classes)]
        if classpath:
            command.extend(("-cp", classpath))
        result = self.capture([*command, *(str(path) for path in production), *paths])
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def capture(
        self, command: list[str], environment=None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self.root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def run(
        self, main: str, *args: str, environment=None
    ) -> subprocess.CompletedProcess[str]:
        return self.capture(
            [self.java, "-cp", self.classpath, main, *args], environment
        )
