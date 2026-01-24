#!/usr/bin/env python3
"""
FastAPI Backend for OWASP-Tester
- Start scans in background
- Expose status + absolute report links
- Serve reports statically at /reports
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Import scanner core (run + save + load config)
from packages.core.wvscanner_core import run_scan, save_report, load_config

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
# repo root: .../owasp-tester/
BASE_DIR = Path(__file__).resolve().parents[2]
CORE_DIR = BASE_DIR / "packages" / "core"
REPORT_DIR = CORE_DIR / "reports"
DEFAULT_CONFIG = CORE_DIR / "config.yaml"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# In-memory scan registry
# scans[scan_id] = {"id": scan_id, "url": target, "status": "running"|"done", "json_path": str, "html_path": str}
scans: Dict[str, Dict[str, Any]] = {}

# --------------------------------------------------------------------------------------
# FastAPI app + CORS
# --------------------------------------------------------------------------------------
app = FastAPI(title="OWASP Tester API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve reports folder (so links can be absolute and simple)
app.mount("/reports", StaticFiles(directory=str(REPORT_DIR)), name="reports")


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _resolve_scan(scan_id: str) -> Dict[str, Any]:
    scan = scans.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


def _run_scan_task(scan_id: str, target_url: str, config_path: str | None = None):
    """Worker: run scan and save reports."""
    cfg_path = str(DEFAULT_CONFIG if not config_path else config_path)
    cfg = load_config(cfg_path)
    result = run_scan(target_url, cfg)
    json_path, html_path = save_report(result, str(REPORT_DIR), report_cfg=cfg.get("report", {}))

    scans[scan_id]["status"] = "done"
    scans[scan_id]["json_path"] = json_path
    scans[scan_id]["html_path"] = html_path


# --------------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------------
@app.get("/")
def root():
    return {"ok": True, "message": "OWASP Tester API running", "reports_dir": str(REPORT_DIR)}


@app.post("/scan/start")
def start_scan(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    body: {"url": "...", "config_path": "optional/custom/config.yaml"}
    """
    target = (data or {}).get("url")
    if not target:
        raise HTTPException(status_code=400, detail="Missing 'url'")

    config_path = (data or {}).get("config_path")
    if config_path:
        cfg_file = Path(config_path)
        if not cfg_file.is_file():
            raise HTTPException(status_code=400, detail=f"Config not found: {config_path}")

    scan_id = str(uuid.uuid4())[:8]
    scans[scan_id] = {"id": scan_id, "url": target, "status": "running"}

    background_tasks.add_task(_run_scan_task, scan_id, target, config_path)
    return {"scan_id": scan_id, "status": "running", "target": target}


@app.get("/scan/{scan_id}/status")
def get_status(scan_id: str):
    """
    returns: {"id": "...", "url": "...", "status": "running|done", ...}
    """
    return _resolve_scan(scan_id)


@app.get("/scan/{scan_id}/links")
def get_links(scan_id: str):
    """
    returns absolute URLs for the frontend buttons.
    """
    scan = _resolve_scan(scan_id)
    html_path = scan.get("html_path")
    json_path = scan.get("json_path")
    if not html_path or not json_path:
        raise HTTPException(status_code=404, detail="Reports not ready yet")

    base = "http://localhost:8000"
    html_name = os.path.basename(html_path)
    json_name = os.path.basename(json_path)
    return JSONResponse({
        "scan_id": scan_id,
        "html_url": f"{base}/reports/{html_name}",
        "json_url": f"{base}/reports/{json_name}",
    })


@app.get("/scan/{scan_id}/report.html")
def get_report_html(scan_id: str):
    scan = _resolve_scan(scan_id)
    path = scan.get("html_path")
    if not path or not Path(path).is_file():
        raise HTTPException(status_code=404, detail="HTML report not found")
    return FileResponse(path, media_type="text/html")


@app.get("/scan/{scan_id}/report.json")
def get_report_json(scan_id: str):
    scan = _resolve_scan(scan_id)
    path = scan.get("json_path")
    if not path or not Path(path).is_file():
        raise HTTPException(status_code=404, detail="JSON report not found")
    return FileResponse(path, media_type="application/json")
