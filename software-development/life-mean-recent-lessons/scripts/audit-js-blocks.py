"""Vérifie la syntaxe JS de CHAQUE bloc <script> d'un fichier HTML.

Usage:
    python audit-js-blocks.py experiments/ui/dashboard.html

Pourquoi bloc par bloc : un seul SyntaxError rend son <script> entier inopérant
(fonctions jamais définies, onglets/boutons inertes) alors que le reste de la page
fonctionne. Le navigateur ne signale rien dans le terminal : ce script est le seul
moyen rapide de le voir. Un `const` redéclaré dans la même portée ne peut pas passer
`node --check`, donc un OK prouve aussi l'absence de doublon.

Nécessite `node` dans le PATH. Code de sortie 1 si un bloc est invalide.
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
    print(f"{len(blocks)} bloc(s) <script> trouvé(s)")

    rc = 0
    for index, js in enumerate(blocks, 1):
        # Position du bloc dans le fichier, utile pour aller corriger au bon endroit.
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
            print(f"  [KO] bloc {index} (à partir de la ligne ~{line}):")
            for text_line in proc.stderr.strip().splitlines()[:4]:
                print("       " + text_line)
        else:
            print(f"  [OK] bloc {index} ({len(js)} caractères)")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        raise SystemExit(2)
    raise SystemExit(check(sys.argv[1]))
