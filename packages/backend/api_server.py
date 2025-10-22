#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Dict, List, Optional

import orjson
import yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

# import scanner core from sibling package
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
import wvscanner_core as core  # noqa: E402

API_TITLE = "Mini-OWASP API"
FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "core", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

class ScanStatus(BaseModel):
    scan_id: str
    target: str
    started_at: float
    finished_at: float | None = None
    state: str = Field(default="running")   # running|finished|error
    progress: int = Field(default=0)        # best-effort
    message: str = Field(default="")
    pages: int = 0
    forms: int = 0
    findings: int = 0
    json_path: str | None = None
    html_path: str | None = None
    events: List[str] = Field(default_factory=list)

RUNS: Dict[str, ScanStatus] = {}
LOCK = asyncio.Lock()

app = FastAPI(title=API_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    config_path: str = os.path.join(os.path.dirname(__file__), "..", "core", "config.yaml")
    details: bool = True

def _progress_emit(st: ScanStatus, msg: str):
    st.events.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(st.events) > 500:
        st.events = st.events[-500:]

async def _run_scan_async(scan_id: str, req: ScanRequest):
    async with LOCK:
        st = RUNS.get(scan_id)
    if not st:
        return
    _progress_emit(st, f"Starting scan for {req.url}")
    try:
        with open(req.config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        _progress_emit(st, "Config loaded.")

        _progress_emit(st, "Initializing scanner...")
        result = core.run_scan(req.url, cfg)

        st.pages = result.crawled_pages
        st.forms = result.discovered_forms
        st.findings = len(result.findings)

        json_path, html_path = core.save_report(result, cfg.get("report", {}).get("out", "reports"), cfg.get("report", {}))
        st.json_path = json_path
        st.html_path = html_path

        _progress_emit(st, f"Reports saved: {json_path} | {html_path}")
        st.progress = 100
        st.state = "finished"
        st.finished_at = time.time()
        _progress_emit(st, "Scan finished.")
    except Exception as e:
        st.state = "error"
        st.message = f"{type(e).__name__}: {e}"
        st.finished_at = time.time()
        _progress_emit(st, f"Scan failed: {st.message}")

@app.get("/healthz")
def healthz():
    return {"ok": True, "time": time.time()}

@app.post("/scan")
async def start_scan(req: ScanRequest, bg: BackgroundTasks):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="url is required")
    scan_id = uuid.uuid4().hex[:12]
    st = ScanStatus(
        scan_id=scan_id,
        target=req.url.strip(),
        started_at=time.time(),
        state="running",
        progress=5,
    )
    RUNS[scan_id] = st
    bg.add_task(_run_scan_async, scan_id, req)
    return {"scan_id": scan_id}

@app.get("/scan/{scan_id}/status")
async def scan_status(scan_id: str):
    st = RUNS.get(scan_id)
    if not st:
        raise HTTPException(status_code=404, detail="scan not found")
    return JSONResponse(st.model_dump(), dumps=orjson.dumps)

@app.get("/scan/{scan_id}/stream")
async def scan_stream(scan_id: str):
    st = RUNS.get(scan_id)
    if not st:
        raise HTTPException(status_code=404, detail="scan not found")

    async def event_gen():
        last = 0
        yield f"event: status\ndata: {json.dumps(st.model_dump())}\n\n"
        while True:
            await asyncio.sleep(0.7)
            cur = len(st.events)
            if cur != last:
                for i in range(last, cur):
                    yield f"event: log\ndata: {json.dumps(st.events[i])}\n\n"
                last = cur
            yield f"event: status\ndata: {json.dumps({'state': st.state, 'progress': st.progress, 'pages': st.pages, 'forms': st.forms, 'findings': st.findings})}\n\n"
            if st.state in ("finished", "error"):
                break

    headers = {"Cache-Control": "no-cache", "Content-Type": "text/event-stream", "Connection": "keep-alive"}
    return StreamingResponse(event_gen(), headers=headers)

def _read_text(path: Optional[str]) -> str:
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="report not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/scan/{scan_id}/report.json")
async def report_json(scan_id: str):
    st = RUNS.get(scan_id)
    if not st or not st.json_path:
        raise HTTPException(status_code=404, detail="json report not found (maybe still running?)")
    txt = _read_text(st.json_path)
    return PlainTextResponse(txt, media_type="application/json")

@app.get("/scan/{scan_id}/report.html")
async def report_html(scan_id: str):
    st = RUNS.get(scan_id)
    if not st or not st.html_path:
        raise HTTPException(status_code=404, detail="html report not found (maybe still running?)")
    txt = _read_text(st.html_path)
    return HTMLResponse(txt)

# Run: uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
