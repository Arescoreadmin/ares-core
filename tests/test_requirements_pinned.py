from pathlib import Path
import re

RE_PINNED = re.compile(r"^\s*([A-Za-z0-9_.-]+)==[0-9]" )


def test_requirements_are_pinned():
    root = Path(__file__).resolve().parents[1]
    req_files = list(root.glob("*/requirements.txt"))
    assert req_files, "No requirements files found"
    for req in req_files:
        for line in req.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            assert RE_PINNED.match(line), f"Unpinned requirement in {req}: {line}"
