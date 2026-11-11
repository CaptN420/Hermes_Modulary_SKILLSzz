# FastAPI test & E2E harness patterns

Copy-paste building blocks that avoid the flaky/deadlocking traps.

## HTTP integration without TestClient
`TestClient` spawns a portal thread per instance; several over the same app (or one per test) intermittently deadlock on Windows. Use the async HTTPX transport instead — no portal, no lifespan, coexists with any module-level TestClient:

```python
import asyncio, httpx
from httpx import ASGITransport

import summarizer.api as api   # the real app

def req(method: str, url: str, **kw) -> httpx.Response:
    async def go():
        transport = ASGITransport(app=api.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            return await ac.request(method, url, **kw)
    return asyncio.run(go())
```

## Isolate settings/store singletons per test
A module singleton stays pointed at a test's already-deleted `tmp_path` for later files. Point it at a fresh temp dir each test and reset in teardown:

```python
import summarizer.settings as S
from summarizer.settings import StudioSettings

@pytest.fixture()
def env(tmp_path, monkeypatch):
    s = StudioSettings(base_dir=tmp_path, lm_enabled=False)
    s.ensure_dirs()
    S._settings = s                # point the singleton at temp
    monkeypatch.setattr(api, "STORE", make_tmp_store(s))
    yield
    S._settings = None             # reset so later files use defaults
```

## Browser E2E file upload (CDP)
From `browser_exec`: set the input's files via CDP, then dispatch `change` so the SPA's handler runs. The file must be a native Windows path; MSYS paths are not translated for native tools.

```python
node_id = cdp("DOM.querySelector", nodeId=cdp("DOM.getDocument")["root"]["nodeId"], selector="#file-input")["nodeId"]
cdp("DOM.setFileInputFiles", nodeId=node_id, files=[r"C:\path\to\file.pdf"])
js("(() => { const i=document.querySelector('#file-input'); i.dispatchEvent(new Event('change',{bubbles:true})); })()")
```

Then **poll** for the visible progress/status transition (the metadata record reaches its terminal state), never `time.sleep` a fixed amount. In the SPA the frontend caches a snapshot taken at creation — re-fetch the resource after a background job finishes instead of trusting the creation response.

## Restart-resume verification
After a long job (analysis) completes, restart the server process and confirm the already-imported doc can be summarized/answered *without* re-running the pipeline. This only works if the in-memory index/registry is rebuilt lazily from the persisted work file — see the `set_index` / `cancel` no-op pitfall in SKILL.md.
