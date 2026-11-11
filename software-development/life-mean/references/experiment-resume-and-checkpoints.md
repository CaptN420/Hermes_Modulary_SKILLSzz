# Experiment engine: checkpoints, resumption, honest “Continue”

Trigger: `continue_experiment`, interrupted or long runs, per-task progress,
resume-after-crash, “the Continue button restarted everything”.

## Contract

- **Continue resumes; it never silently restarts.** Branch explicitly:
  no checkpoint → refuse with a reason; run already finished → refuse
  (“already finished (N/N tasks)”) and point at restart; seed/domain changed since the
  interruption → refuse, because resuming would mix two experiments.
- **RAW evidence first, checkpoint line second.** A task may only be skipped on
  resume if its evidence exists on disk. Writing the checkpoint first makes the
  resume skip a task whose result never materialised.
- **Metrics are cumulative across a resume**: `completed = prior + new`,
  `pass_rate = valid / completed`. Resetting counters on Continue is what made the
  old “continue” a restart in disguise.
- **Archive the previous checkpoint** (`.jsonl.bak`), never delete it — same NO DELETE
  rule that governs the rest of the project.
- **The API carries the reason.** Refusals answer `409 <reason>_refused` with the
  controller's recorded message, not a generic 500; the UI surfaces `data.error`.
  A refusal the user cannot read is indistinguishable from a bug.

## Identity: index + content fingerprint, never task id

- Generated task ids are random UUIDs, so the same seed regenerates the same content
  under different ids. Match on the task's **index plus a fingerprint of its content**
  (domain, difficulty, description, ground_truth), and on resume regenerate the batch
  and compare every recorded index before executing anything. A mismatch is a refusal,
  not a best-effort merge.
- Store the meta line (total, seed, domain, mode) as the first line of the checkpoint so
  the cheap config check happens before regenerating a batch.

## Measuring a real interruption (do not fake it)

- Deterministic tasks finish faster than an HTTP round trip (a few hundred tasks in
  well under a second), so `start; sleep; stop` over HTTP usually lands *after* the run
  completed. Raise the batch to a few thousand tasks so the stop lands mid-run — that is
  what produced a genuine 975/4000 stop and a resumed 4000/4000.
- Field numbers to check: checkpoint lines = tasks done + 1 meta line; RAW lines =
  tasks done. After the resume both reach the total with **no duplicates** — that is the
  proof nothing executed twice.
- For a deterministic test, inject the stop from a wrapped `run_task` after the Nth call
  instead of racing HTTP.

## Test seam

- When the loop moves from `run_batch` to per-task `run_task`, a mock that patches
  `run_batch` keeps returning a whole batch per task and the counts double.
  Move the fake to `run_task` with a `side_effect=[…]` list, **keep every original
  assertion**, and add a call-count assertion (`run_task.call_count == n`). Then state
  the seam change in the report: adapting a fake is not weakening a test, hiding it is.
- Wait for the worker by checking `exp_id not in controller._worker_threads`, not
  `is_running is False`: `stop_experiment` flips that flag immediately while the worker
  is still finishing its current task.
- Isolate runs: `LIFE_MEAN_RUNS_DIR` for summaries/checkpoints, and `monkeypatch.chdir`
  for tests, because the RAW root follows the process cwd by design.

## Pitfalls

- A stop flag checked **between** tasks means “stop” completes the task in flight. That
  is correct atomicity — describe it that way, do not claim instant cancellation.
- Per-task persistence changes failure semantics: one failed RAW write marks the run
  FAILED mid-way. Keep that behaviour (no silent evidence loss) and let the checkpoint
  show exactly how far it got.

## Engine timeouts: bounded work, never a bounded lie

Three layers, each with its own guard — having one is not having the others.

- **Task.** `task_timeout_seconds` (0 disables). Run the task in a daemon thread and
  `join(limit)`; on expiry return an explicit `TASK_TIMEOUT` result
  (`answer=None`, `is_valid=False`, `metadata.timed_out=True`) with the limit in the
  message. A timeout is a failure record, not an empty answer and not a success.
- **Double counting.** Python cannot kill a thread, so an expired worker keeps running.
  Move `self._results.append(...)` out of the task implementation and into the wrapping
  `run_task`: the orphan then has nowhere to append, and statistics cannot count one
  task twice. Verify by sleeping past the deadline and asserting `len(_results) == 1`.
- **Run.** `run_timeout_seconds` (0 disables) checked between tasks: stop cleanly, record
  `RUN_TIMEOUT` with the index reached, and leave the checkpoint resumable. State the
  semantics you chose — a per-segment limit that re-arms on each resume is defensible,
  but a user who resumes expects a total budget unless told otherwise.
- **Provider.** `OpenAI(base_url=…, api_key=…)` defaults to 600 s *with* retries: pass
  `timeout=` and `max_retries=0` to the client **and** `timeout=` on every request, or a
  single stalled backend freezes a debate for minutes. Map the failure to
  `finish_reason="timeout"` and an explicit `[LLM_TIMEOUT …]` text; never let it fall
  through as a normal empty completion. Make the default overridable by env
  (`LIFE_MEAN_LLM_TIMEOUT_SECONDS`).
- **Config plumbing is part of the feature.** A new key must exist in the `ExperimentConfig`
  dataclass, `to_dict`, `from_dict` **and** the dashboard's `_validate_experiment_input`
  whitelist; otherwise `ExperimentConfig(**data)` raises and the API answers 400, leaving
  the guard unreachable from the UI while tests still pass.
- **Measure with a real backend, not just mocks.** Normal call vs `timeout=0.001` gives
  `finish_reason` `length`/`timeout` respectively; over HTTP a `run_timeout_seconds=2` on a
  several-thousand-task run stops mid-way and `continue` resumes from the checkpoint.
- **Say the limit out loud:** an expired task still burns CPU/IO until it finishes on its
  own, and an orphaned thread is not cancelled — only ignored.
