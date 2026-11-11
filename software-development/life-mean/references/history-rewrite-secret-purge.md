# Purging a leaked secret from git history (git filter-repo, force-push, resync)

Use when a credential/API-key fragment is committed anywhere in the repo's HISTORY (not just the working tree) and must be erased. A working-tree delete is NOT enough — the secret survives in every commit that ever contained it, and a public remote still serves it.

## 1. Audit scope FIRST (know exactly what to scrub)
- Find the introducing commit for one literal: `git log --all -S'<fragment>' -- <path>`
- Scan ALL blobs in ALL commits for the pattern family:
  ```bash
  git rev-list --all | while read c; do git grep -oIE 'sk-lm-[A-Za-z0-9]{4,}|ghp_[A-Za-z0-9]{4,}|gho_[A-Za-z0-9]{4,}|github_pat_[A-Za-z0-9_]{4,}|sk-[A-Za-z0-9]{30,}' "$c" 2>/dev/null; done | awk '!seen[$0]++'
  ```
  Distinct real tokens (not the `***` REDACT marker, not truncated `sk-lm-...NNNN` test fixtures, not the `_re.compile` redaction regexes themselves) are your scrub list.
- `git grep --cached` greps the WHOLE index (every tracked file), NOT just the files staged in the current commit — you cannot use it to prove "this commit added nothing". Scope to the commit's actual additions:
  ```bash
  git diff --cached --name-only -z | xargs -0 -I{} sh -c 'git show :"{}" 2>/dev/null | grep -lE "<pat>" >/dev/null 2>&1 && echo "{}"'
  ```
  (empty = no secret in the staged additions).
- `historical/` is git-tracked and NOT covered by the `.gitignore` entries that protect `legacy/`/`External/` — a masked-but-real fragment like `api_key = "***:kHwVc0J..."` in a `historical/.../config.py` is a real leak even though it looks pre-masked.

## 2. Install + invoke filter-repo on this host
- Not a git subcommand by default: `python -m pip install git-filter-repo`.
- The exe lands in the Python `Scripts` dir whose version string is DISPLAY-MASKED in tool output (e.g. `python-3.14.7+202****0901-win32-x64`) — you cannot type it literally. Resolve it via bash glob so the real path is used:
  ```bash
  FREXE=$(ls -d /c/Users/<user>/AppData/Local/hermes/tools/python-3.14*/Scripts/git-filter-repo.exe | head -1)
  ```

## 3. Backup, then rewrite
- Backup content (NOT the secret): `git tag secret-purge-backup-$(date +%Y%m%d-%H%M%S) main` (filter-repo rewrites ALL refs incl. backups, so the secret ends up gone everywhere; the backup only protects content).
- Replace-text file (one literal per line; `literal==>replacement` replaces in place, a line WITHOUT `==>` deletes its whole containing line):
  ```
  kHwVc0J33rwUC0lMh7xn==>REDACTED
  sk-lm-eT==>sk-lm-REDACTED
  ```
- Run: `"$FREXE" --force --replace-text .secret_repl.txt` (`--force` is required because the repo is not a fresh clone).
- filter-repo REMOVES the `origin` remote — re-add it afterwards.

## 4. Verify thoroughly (working tree + every commit + remote)
```bash
git rev-list --all | while read c; do git grep -l '<fragment>' "$c"; done | sort -u   # must be empty
git show origin/main:<path> | grep api_key   # confirm REDACTED on the remote blob
```

## 5. The history rewrite now changes ALL subsequent SHAs
- Existing clones diverge. Mandate a resync in a README notice and forbid force-pushing an old branch (it would re-introduce the secret):
  ```bash
  # no local work:  git fetch origin main && git reset --hard origin/main
  # has local branches: re-clone
  ```
- Push ONLY with the documented wincred bypass and `--force-with-lease` after confirming the remote is still at the old sha (`git fetch origin <branch>`):
  `git -c credential.helper= -c credential.helper="<wincred.exe>" push --force-with-lease=main:<old_sha> origin main`

## 6. Rotate, don't just scrub
A fragment that touched a PUBLIC repo may have been copied; a history purge does not revoke the credential. Have the user replace/revoke the original key (e.g. in `.env` / LM Studio / provider dashboard) and confirm the new one is on a git-ignored path.
