#!/usr/bin/env python3
"""
Mini OWASP Web Scanner — CLI (v1.3, JS-aware)
- Colored, detailed console output
- --details: show pages, forms, and grouped findings
- --debug:   verbose logging for crawl / requests
- --no-js:   override config to disable Playwright/JS rendering quickly
- --js-discovery: extra Playwright pass to auto-visit SPA routes and extract Angular-style forms
- --routes:  comma-separated list of SPA routes to visit during js-discovery
- NEW: Merge js-discovery pages/forms back into ScanResult before saving reports.
"""

import argparse
import logging
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import urllib.parse as urlparse

import yaml  # PyYAML
from colorama import Fore, Style, init as colorama_init

from wvscanner_core import run_scan, save_report, summary_text

try:
    from js_renderer import js_context, render_url
    JS_AVAILABLE = True
except Exception:
    JS_AVAILABLE = False

colorama_init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("wvscanner_cli")


def load_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        log.info("Loaded config from %s", path)
        return cfg
    except Exception as e:
        log.error("Failed reading config %s: %s", path, e)
        sys.exit(1)

def norm_url(u: str) -> str:
    try:
        p = urlparse.urlsplit(u)
        if not p.scheme:
            return "http://" + u
        return u
    except Exception:
        return u

def unique_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def js_discovery_pass(base_url: str,
                      routes: List[str],
                      js_cfg: Dict) -> Tuple[List[str], Dict[str, List[Dict[str, Any]]]]:
    if not JS_AVAILABLE:
        log.warning("Playwright is not available; skipping --js-discovery pass.")
        return [], {}

    headless = bool(js_cfg.get("headless", True))
    nav_timeout_ms = int(js_cfg.get("nav_timeout_ms", 12000))
    run_timeout_ms = int(js_cfg.get("run_timeout_ms", 4000))
    max_body_chars = int(js_cfg.get("max_body_chars", 200000))

    targets = [base_url]
    for r in routes:
        r = r.strip()
        if not r:
            continue
        targets.append(urlparse.urljoin(base_url, r))

    pages: List[str] = []
    forms: Dict[str, List[Dict[str, Any]]] = {}

    try:
        with js_context(headless=headless) as browser:
            for t in targets:
                try:
                    res = render_url(browser, t, nav_timeout_ms, run_timeout_ms, max_body_chars)
                    pages.append(t)
                    if res.forms:
                        forms[t] = res.forms
                    log.debug("[js-discovery] %s -> forms=%d", t, len(res.forms or []))
                except Exception as e:
                    log.debug("[js-discovery] error for %s: %s", t, e.__class__.__name__)
                    continue
    except Exception as e:
        log.warning("Playwright could not start for discovery: %s", e.__class__.__name__)

    return unique_preserve_order(pages), forms

def print_colored_summary(result):
    high = [f for f in result.findings if f.severity == "HIGH"]
    med = [f for f in result.findings if f.severity == "MEDIUM"]
    info = [f for f in result.findings if f.severity in ("LOW", "INFO")]

    print()
    print(Fore.CYAN + f"=== Scan Summary for {result.target} ===" + Style.RESET_ALL)
    print(f"Pages crawled: {Fore.YELLOW}{result.crawled_pages}{Style.RESET_ALL} | Forms: {Fore.YELLOW}{result.discovered_forms}{Style.RESET_ALL}")
    print(f"{Fore.RED}HIGH:{Style.RESET_ALL} {len(high)}  {Fore.YELLOW}MEDIUM:{Style.RESET_ALL} {len(med)}  {Fore.BLUE}INFO:{Style.RESET_ALL} {len(info)}")
    print()

    by_cat = defaultdict(list)
    for f in result.findings:
        by_cat[f.category].append(f)

    if not result.findings:
        print(Fore.GREEN + "No findings — nice! 😄" + Style.RESET_ALL)
        return

    print(Fore.MAGENTA + "Findings by category:" + Style.RESET_ALL)
    for cat, items in sorted(by_cat.items(), key=lambda x: (-len(x[1]), x[0])):
        color = Fore.YELLOW if any(i.severity == "MEDIUM" for i in items) else Fore.RED if any(i.severity == "HIGH" for i in items) else Fore.CYAN
        print(f"  {color}{cat}{Style.RESET_ALL}: {len(items)}")
    print()

def print_detailed(result, max_show_per_cat=20, extra_pages=None, extra_forms=None):
    print(Fore.BLUE + "Crawled pages (top):" + Style.RESET_ALL)
    for p in result.pages[:50]:
        print("  -", p)
    if len(result.pages) > 50:
        print(f"  ... ({len(result.pages) - 50} more pages)")
    print()

    if extra_pages:
        print(Fore.BLUE + "JS-discovery pages (not part of vuln modules yet):" + Style.RESET_ALL)
        for p in extra_pages[:50]:
            print("  +", p)
        if len(extra_pages) > 50:
            print(f"  ... ({len(extra_pages) - 50} more JS-discovery pages)")
        print()

    print(Fore.BLUE + "Forms discovered (page -> inputs):" + Style.RESET_ALL)
    if not result.forms:
        print("  (no HTML/GET forms discovered by crawler)")
    else:
        for page, forms in result.forms.items():
            print(f"  {page} -> {len(forms)} form(s)")
            for fi, form in enumerate(forms, start=1):
                inputs = ", ".join(form.get('inputs', {}).keys()) if form.get('inputs') else "(no inputs)"
                print(f"    [{fi}] {form.get('method','get').upper()} {form.get('action')}   inputs: {inputs}")
    print()

    if extra_forms:
        print(Fore.BLUE + "JS-discovery forms (Angular/SPA):" + Style.RESET_ALL)
        for page, forms in extra_forms.items():
            print(f"  {page} -> {len(forms)} form(s)")
            for fi, form in enumerate(forms, start=1):
                inputs = ", ".join(form.get('inputs', {}).keys()) if form.get('inputs') else "(no inputs)"
                print(f"    [{fi}] {form.get('method','get').upper()} {form.get('action')}   inputs: {inputs}")
        print()

    if not result.findings:
        return
    by_cat = defaultdict(list)
    for f in result.findings:
        by_cat[f.category].append(f)
    for cat in sorted(by_cat.keys()):
        items = by_cat[cat]
        print(Fore.MAGENTA + f"--- {cat} ({len(items)}) ---" + Style.RESET_ALL)
        items_sorted = sorted(items, key=lambda x: ("0" if x.severity=="HIGH" else "1" if x.severity=="MEDIUM" else "2", x.url))
        for idx, f in enumerate(items_sorted[:max_show_per_cat], start=1):
            sev_color = Fore.RED if f.severity == "HIGH" else (Fore.YELLOW if f.severity == "MEDIUM" else Fore.CYAN)
            print(f" {sev_color}[{f.severity}]{Style.RESET_ALL} {f.url}  param={Fore.GREEN}{f.param}{Style.RESET_ALL}")
            print(f"    evidence: {f.evidence}")
        if len(items) > max_show_per_cat:
            print(f"    ... ({len(items) - max_show_per_cat} more findings in category {cat})")
        print()

def parse_args():
    ap = argparse.ArgumentParser(description="Mini OWASP Web Vulnerability Scanner (CLI)")
    ap.add_argument("--url", required=True, help="Target URL (e.g., http://testphp.vulnweb.com/)")
    ap.add_argument("--config", default="config.yaml", help="Config YAML path")
    ap.add_argument("--out", default="reports", help="Output directory for reports")
    ap.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    ap.add_argument("--details", action="store_true", help="Print detailed findings (pages + per-category lists)")
    ap.add_argument("--no-js", action="store_true", help="Override config to disable JavaScript rendering")
    ap.add_argument("--js-discovery", action="store_true", help="Run an extra Playwright pass to visit SPA routes and extract forms (non-destructive)")
    ap.add_argument(
        "--routes",
        default="#/login,#/register,#/search,#/contact,#/about",
        help="Comma-separated SPA routes to visit during --js-discovery (joined to base URL)"
    )
    return ap.parse_args()

def main():
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug("Debug logging enabled")

    cfg = load_config(args.config)

    if args.no_js:
        if "javascript" not in cfg:
            cfg["javascript"] = {}
        cfg["javascript"]["enabled"] = False
        log.info("--no-js: JavaScript rendering disabled by CLI override")

    # Run core scan first
    res = run_scan(args.url, cfg)

    extra_pages = []
    extra_forms = {}

    # Optional JS discovery pass
    if args.js_discovery:
        js_cfg = cfg.get("javascript", {}) or {}
        if not js_cfg.get("enabled", False):
            log.warning("--js-discovery requested but javascript.enabled is false. Enable JS or drop --no-js.")
        elif not JS_AVAILABLE:
            log.warning("--js-discovery requested but Playwright is not available in this environment.")
        else:
            routes = [r.strip() for r in (args.routes or "").split(",")]
            base = norm_url(args.url)
            log.info("Starting JS discovery pass on %d route(s)...", len([r for r in routes if r]))
            ep, ef = js_discovery_pass(base, routes, js_cfg)
            # For printing in --details
            extra_pages = unique_preserve_order([p for p in ep if p not in res.pages])
            extra_forms = ef or {}

            # ---- NEW: merge discovery results back into the ScanResult before saving
            # Merge pages
            res.pages = unique_preserve_order(res.pages + extra_pages)
            res.crawled_pages = len(res.pages)

            # Merge forms (append to any existing per-page lists)
            for page, forms_list in extra_forms.items():
                if not forms_list:
                    continue
                if page not in res.forms:
                    res.forms[page] = []
                res.forms[page].extend(forms_list)

            # Recompute discovered_forms
            res.discovered_forms = sum(len(v) for v in res.forms.values())

    # Print summary + optional details
    print_colored_summary(res)
    if args.details:
        print_detailed(res, max_show_per_cat=25, extra_pages=extra_pages, extra_forms=extra_forms)

    # Save reports (now include merged forms/pages)
    json_path, html_path = save_report(res, args.out, cfg.get("report", {}))
    print(f"[+] Reports saved: {json_path or '(JSON disabled)'} | {html_path or '(HTML disabled)'}")

if __name__ == "__main__":
    main()
