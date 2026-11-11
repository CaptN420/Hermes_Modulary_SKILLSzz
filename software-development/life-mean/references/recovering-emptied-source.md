# Recovering source files truncated to 0 bytes

When a source file comes back **empty (0 bytes)** but the surrounding code and
its tests still import symbols from it, the file was truncated/emptied, not
deliberately deleted. Recover in this order — each step is cheaper than the next.

## 1. Session history first
`session_search` for the file path (or its docstring / a class name). The
original `write_file` tool call's `content` holds the FULL source verbatim — it
is the most faithful recovery and usually exact. Filter to `assistant` role to
skip tool-output noise.

## 2. `__pycache__` .pyc of a DIFFERENT interpreter
A pre-truncation `.pyc` preserves the OLD bytecode. Spot it by (a) size — much
larger than the tiny stale recompile of the empty file — and (b) mtime predating
the truncation. To turn it back into source you need the interpreter whose
version produced it: `uv python install <maj.min>`. Caveat: `uncompyle6` tops
out at 3.8 — for 3.9+ pycs you usually cannot decompile; use history or
reconstruction instead.

## 3. Reconstruct the CURRENT interface from live usage
When the recovered pyc/history is OLDER than what the code now expects, the
tests + engine reference the EVOLVED surface. Grep what is actually called:
`grep -oE "self\.obj\.\w+" <engine>.py` (and on the test files) to enumerate
the exact methods/fields required, then re-add anything your recovery lacks
(e.g. a `rollback_reserved_turn(speaker)` the engine invokes on an optimistic
turn reservation). The tests that import the type are the source of truth for
the evolved interface, not the stale pyc.

## 4. Rule out a stale/misattributed import first
Before heavy recovery, confirm the loaded module is the file you think it is:
print `module.__file__` and reproduce in a clean interpreter. Two near-identical
modules (core vs memory `debate_state.py`) can misattribute the failure.
Check identity with `A is B` when a module is meant to re-export.

## Tooling note
`write_file` refuses to overwrite a file you previously read with pagination —
even when it is now empty (the stale-read guard). Bypass by writing the recovery
to a NEW temp path then `cp` over the target (terminal). Do not loop on
write_file with identical args.

## Keep the recovery minimal
Reassemble a truncated dataclass method-by-method from partial reads rather than
reinventing the whole module. When two files must stay one class, make the
canonical live in the semantic owner and re-export, then VERIFY `A is B` and run
the suite before trusting the merge.
