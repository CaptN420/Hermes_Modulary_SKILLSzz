# Incremental ingestion of JSONL logs — offsets, caps, idempotence

Mechanics to respect for any ingester that resumes a log file where it stopped
(the Life_mean_realm Pipeline Inspector and any equivalent).

## 1. Returned offsets must be ABSOLUTE

Classic trap:

```python
fh.seek(start_offset)
pos = 0                      # ← the bug
while (chunk := fh.readline()):
    pos += len(chunk)
    yield ev, pos            # offset relative to the resume point
```

The caller stores `pos` as an absolute position. On the next resume, the offset has *shrunk*:
the reader restarts in the middle of a line, re-reads content already consumed, or stops at the wrong
place — without raising an exception.

Fix: read from the start, skip fully consumed lines, return the real position.

```python
pos = 0
line_no = 0
while (chunk := fh.readline()):
    pos += len(chunk)
    line_no += 1
    if pos <= start_offset:      # line already consumed
        continue
    if not chunk.endswith(b"\n"):  # partial line: do not consume it
        break
    yield line_no, chunk.decode("utf-8", errors="replace").strip(), pos
```

Linear cost accepted (≈1 s for 85 MB); offset and line-number correctness comes first.
Recording the real `line_no` also makes `source_line` usable to trace back to the original log.

## 2. A per-file cap requires a flag, otherwise the rest is lost

A `max_records_per_file` (e.g. 200,000) cuts off the reading of a large file. If the state persists
`size == st_size` with no other mark, the next pass considers the file fully
consumed and **never reads the remainder**. No error is reported.

- Add a `truncated` column (migration `ALTER TABLE ingest_state ADD COLUMN truncated INTEGER NOT NULL DEFAULT 0`).
- The "file already ingested" condition must include `and not state['truncated']`.
- Record the `offset` of the last emitted record, not the file size.
- Explicit error message: `cap N reached (resume at offset X)`.

Repair an inherited state: `UPDATE ingest_state SET truncated=1 WHERE events >= <cap>`.
Then check that `offset == size` and `truncated == 0`: that is the proof that the file really
is consumed in full. A file larger than the cap requires **two passes** —
document it instead of letting it look like a complete ingestion in a single run.

## 3. Idempotence and deduplication

- Stable `event_id` (hash of type + file + line + timestamp) and `INSERT OR IGNORE`.
- Check: `SELECT count(*) - count(distinct event_id) FROM events` must equal 0.
- Resume check: two consecutive passes with no change → `events_added == 0`.
- A `bytes_read` counter declared but never incremented reads as a read bug:
  feeding it with the size actually examined makes the passes comparable.

## 4. What the ingester must not do

- Do not rewrite or truncate the original log: the ingestion state is a *derived cache*,
  reconstructible; deleting and rebuilding that cache is acceptable, touching the logs is not.
- Do not infer a causal correlation from a mere grouping identifier. `run_id`,
  `session_id`, `generation_id` prove membership of the same run → **probable** correlation.
  Only a `model_call_id` or an audit `correlation_id` authorise "explicit".

## 5. Quick verification

```python
c.execute("select correlation,count(*) from events group by correlation")
c.execute("select path,offset,size,truncated from ingest_state where truncated=1")
c.execute("select count(*) - count(distinct event_id) from events")
```
