"""Check the JS syntax of EACH <script> block of an HTML file.

Usage:
    python audit-js-blocks.py experiments/ui/dashboard.html

Why block by block: a single SyntaxError makes its whole <script> inoperative
(functions never defined, tabs/buttons inert) while the rest of the page
works. The browser reports nothing in the terminal: this script is the only
fast way to see it. A `const` redeclared in the same scope cannot pass
`node --check`, so an OK also proves the absence of a duplicate.

Requires `node` in the PATH. Exit code 1 if a block is invalid.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def check(path: str) -> int:
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", src, re.S)
    print(f"{len(blocks)} <script> block(s) found")

    rc = 0
    for index, js in enumerate(blocks, 1):
        # Position of the block in the file, useful for fixing it in the right place.
        start = src.find(js)
        line = src[:start].count("\n") + 1 if start >= 0 else 0

        fd, tmp = tempfile.mkstemp(suffix=".js")
        os.close(fd)
        try:
            Path(tmp).write_text(js, encoding="utf-8")
            proc = subprocess.run(
                ["node", "--check", tmp], capture_output=True, text=True
            )
        finally:
            os.unlink(tmp)

        if proc.returncode != 0:
            rc = 1
            print(f"  [KO] block {index} (starting at line ~{line}):")
            for text_line in proc.stderr.strip().splitlines()[:4]:
                print("       " + text_line)
        else:
            print(f"  [OK] block {index} ({len(js)} characters)")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        raise SystemExit(2)
    raise SystemExit(check(sys.argv[1]))
