#!/usr/bin/env python3
# packages/core/wvscanner_core.py
"""
Mini OWASP Web Scanner (Core) — v1.5
- JS-aware crawler (optional Playwright rendering) with SPA canonicalization
- Modules: reflected XSS (basic + DOM-aware), SQLi (basic), Security headers
- Reporting: JSON + HTML (HTML includes Forms section)
- External payloads via config: payloads.xss_files / payloads.sqli_files
- AI-ready: merges payloads from Static + AI providers with caps

NOTE: Use only on assets you own or have explicit permission to test.
"""

from __future__ import annotations

import os
import time
import json
import html
import queue
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
import urllib.parse as urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

# Providers (new)
from payloads.providers.static_provider import StaticPayloadProvider
from payloads.providers.ai_provider_stub import AIPayloadProvider

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

log = logging.getLogger("wvscanner_core")


# -------------------------
# Data models
# -------------------------
@dataclass
class Finding:
    severity: str
    category: str
    url: str
    param: str
    evidence: str

@dataclass
class ScanResult:
    target: str
    pages: List[str]
    forms: Dict[str, List[Dict[str, Any]]]
    crawled_pages: int
    discovered_forms: int
    findings: List[Finding]
    started_at: float
    finished_at: float


# -------------------------
# Utilities
# -------------------------
def norm_url(u: str) -> str:
    try:
        parsed = urlparse.urlsplit(u)
        if not parsed.scheme:
            return "http://" + u
        return u
    except Exception:
        return u

def strip_hash(u: str) -> str:
    p = urlparse.urlsplit(u)
    return urlparse.urlunsplit((p.scheme, p.netloc, p.path, p.query, ""))

def same_host(url_a: str, url_b: str) -> bool:
    try:
        a = urlparse.urlsplit(url_a).netloc
        b = urlparse.urlsplit(url_b).netloc
        return a.lower() == b.lower()
    except Exception:
        return False

def host_in_allowed(host: str, allowed_hosts: List[str]) -> bool:
    if not allowed_hosts:
        return True
    host = (host or "").lower()
    for allowed in allowed_hosts:
        allowed = (allowed or "").lower()
        if host == allowed or (allowed and host.endswith("." + allowed)):
            return True
    return False

def normalize_slash_path(path: str) -> str:
    if not path:
        return "/"
    norm = "/" + path.lstrip("/")
    while "//" in norm:
        norm = norm.replace("//", "/")
    return norm

def canonicalize_spa(u: str, start_origin: str, start_path: str) -> str:
    """Make hash-routes look like canonical paths under the app's base path."""
    p = urlparse.urlsplit(u)
    frag = p.fragment or ""
    path = normalize_slash_path(p.path)
    if f"{p.scheme}://{p.netloc}" == start_origin:
        if frag.startswith("/"):
            base_path = normalize_slash_path(start_path)
            return urlparse.urlunsplit((p.scheme, p.netloc, base_path, "", frag))
        if "#" in u and frag and frag.startswith("/") and path not in ("/", normalize_slash_path(start_path)):
            base_path = normalize_slash_path(start_path)
            return urlparse.urlunsplit((p.scheme, p.netloc, base_path, "", frag))
    return urlparse.urlunsplit((p.scheme, p.netloc, path, p.query, frag))

def canonical_key(u: str) -> str:
    p = urlparse.urlsplit(u)
    path = normalize_slash_path(p.path)
    frag = p.fragment or ""
    return urlparse.urlunsplit((p.scheme, p.netloc, path, p.query, frag))

def should_skip(href: str, excludes_paths: List[str], exclude_domains: List[str]) -> bool:
    try:
        host = urlparse.urlsplit(href).netloc.lower()
    except Exception:
        host = ""
    if host and any(host == d or host.endswith("." + d) for d in exclude_domains):
        return True
    href_l = (href or "").lower()
    return any(e in href_l for e in excludes_paths)

def make_session(user_agent: str,
                 follow_redirects: bool,
                 timeout: int,
                 verify_ssl: bool = True,
                 retries: int = 2,
                 backoff_factor: float = 0.4) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent})
    s.verify = verify_ssl
    s.allow_redirects = follow_redirects
    # custom attribute used by our code
    s.request_timeout = timeout

    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        redirect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST", "HEAD", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


# -------------------------
# Playwright DOM renderer helpers (optional)
# -------------------------
def _try_render_with_js(js_cfg: Dict, url: str):
    try:
        from js_renderer import js_context, render_url
    except Exception:
        return None  # Playwright not available
    headless = bool(js_cfg.get("headless", True))
    nav_timeout = int(js_cfg.get("nav_timeout_ms", 12000))
    run_timeout = int(js_cfg.get("run_timeout_ms", 4000))
    max_chars = int(js_cfg.get("max_body_chars", 200000))
    try:
        with js_context(headless=headless) as browser:
            return render_url(browser, url, nav_timeout, run_timeout, max_chars)
    except Exception:
        return None


# -------------------------
# JS-aware CRAWLER with SPA canonicalization
# -------------------------
def crawl(start_url: str,
          session: requests.Session,
          *,
          max_depth: int,
          same_host_only: bool,
          excludes_paths: List[str],
          exclude_domains: List[str],
          follow_redirect_hosts: bool,
          allowed_hosts: List[str],
          max_pages: int,
          delay_ms: int,
          js_cfg: Optional[Dict] = None) -> Tuple[List[str], Dict[str, List[Dict[str, str]]]]:
    """
    Returns:
      pages: list of unique page URLs visited (canonicalized)
      forms: mapping URL -> list of forms (each: {action, method, inputs: dict})
    """
    pages: List[str] = []
    forms: Dict[str, List[Dict[str, str]]] = {}
    visited_keys: Set[str] = set()

    start_url = norm_url(start_url)
    start_split = urlparse.urlsplit(start_url)
    start_origin = f"{start_split.scheme}://{start_split.netloc}"
    start_path = normalize_slash_path(start_split.path or "/")
    start_host = start_split.netloc.lower()

    use_js = bool(js_cfg and js_cfg.get("enabled", False))

    js_browser_ctx = None
    js_browser = None
    if use_js:
        try:
            from js_renderer import js_context
            js_browser_ctx = js_context(headless=bool(js_cfg.get("headless", True)))
            js_browser = js_browser_ctx.__enter__()
            log.debug("JS renderer (Playwright) initialized.")
        except Exception as e:
            js_browser = None
            js_browser_ctx = None
            log.warning("Failed to initialize Playwright renderer: %s. Falling back to HTML-only crawl.", type(e).__name__)

    q: queue.Queue = queue.Queue()
    q.put((start_url, 0))

    while not q.empty():
        url, depth = q.get()
        url = canonicalize_spa(url, start_origin, start_path)
        key = canonical_key(url)
        if key in visited_keys or depth > max_depth:
            continue

        try:
            resp = session.get(strip_hash(url), timeout=session.request_timeout, allow_redirects=True)
            effective_url = resp.url
            raw_html = resp.text or ""
        except Exception as e:
            log.warning("Fetch failed for %s: %s", url, e.__class__.__name__)
            continue

        requested_host = urlparse.urlsplit(url).netloc.lower()
        effective_host = urlparse.urlsplit(effective_url).netloc.lower()
        if effective_host != requested_host:
            if not follow_redirect_hosts:
                visited_keys.add(key)
                continue
            else:
                url = canonicalize_spa(effective_url, start_origin, start_path)
                key = canonical_key(url)

        this_host = urlparse.urlsplit(url).netloc.lower()
        if same_host_only and this_host != start_host:
            visited_keys.add(key)
            continue
        if not host_in_allowed(this_host, allowed_hosts):
            visited_keys.add(key)
            continue

        visited_keys.add(key)
        pages.append(url)

        if max_pages and len(pages) >= max_pages:
            break

        rendered_html = None
        js_links: List[str] = []
        js_forms: List[Dict[str, str]] = []
        if js_browser is not None:
            try:
                from js_renderer import render_url
                nav_timeout_ms = int(js_cfg.get("nav_timeout_ms", 12000))
                run_timeout_ms = int(js_cfg.get("run_timeout_ms", 4000))
                max_body_chars = int(js_cfg.get("max_body_chars", 200000))
                result = render_url(js_browser, url, nav_timeout_ms, run_timeout_ms, max_body_chars)
                rendered_html = result.html or ""
                js_links = result.links or []
                js_forms = result.forms or []
            except Exception:
                rendered_html = None

        dom_html = rendered_html if rendered_html else raw_html
        soup = BeautifulSoup(dom_html, "lxml")

        # forms from Playwright heuristic first
        page_forms: List[Dict[str, str]] = []
        for jf in js_forms:
            action = jf.get("action") or url
            method = (jf.get("method") or "get").lower()
            inputs = jf.get("inputs") or {}
            if inputs:
                page_forms.append({"action": action, "method": method, "inputs": inputs})

        # then parse static forms
        for form in soup.find_all("form"):
            method = (form.get("method") or "get").lower()
            action = form.get("action") or url
            action = urlparse.urljoin(url, action)
            inputs = {}
            for inp in form.find_all(["input", "textarea", "select"]):
                name = (inp.get("name")
                        or inp.get("formcontrolname")
                        or inp.get("ng-reflect-name")
                        or inp.get("ng-reflect-form-control-name")
                        or inp.get("aria-label")
                        or inp.get("placeholder"))
                if not name:
                    continue
                value = inp.get("value") or ""
                if inp.name.lower() == "select":
                    opt = inp.find("option", selected=True) or inp.find("option")
                    if opt:
                        value = opt.get("value") or (opt.text or "")
                inputs[str(name)] = value
            if inputs:
                page_forms.append({"action": action, "method": method, "inputs": inputs})

        if page_forms:
            forms[url] = page_forms

        # collect links
        link_candidates: List[str] = []
        if js_links:
            link_candidates.extend(js_links)
        for a in soup.find_all("a", href=True):
            link_candidates.append(urlparse.urljoin(url, a["href"]))
        for a in soup.find_all(href=True):
            href = a.get("href")
            if href and href.startswith("#"):
                base = url.split("#", 1)[0]
                link_candidates.append(base + href)

        seen_local: Set[str] = set()
        for href in link_candidates:
            if not href:
                continue
            cand = canonicalize_spa(href, start_origin, start_path)
            ckey = canonical_key(cand)
            if ckey in seen_local or ckey in visited_keys:
                continue
            seen_local.add(ckey)
            if should_skip(cand, [], []):
                continue
            link_host = urlparse.urlsplit(cand).netloc.lower()
            if not host_in_allowed(link_host, allowed_hosts):
                continue
            if same_host_only and not same_host(start_url, cand):
                continue
            q.put((cand, depth + 1))

        if delay_ms:
            time.sleep(delay_ms / 1000.0)

    if js_browser_ctx is not None:
        try:
            js_browser_ctx.__exit__(None, None, None)
        except Exception:
            pass

    return pages, forms


# -------------------------
# Modules: XSS (reflected), SQLi (basic), Headers, DOM-XSS (basic)
# -------------------------
def test_reflected_xss(session: requests.Session, url: str, param: str, payloads: List[str], cap: Optional[int] = None) -> Optional[Finding]:
    tested = 0
    for p in payloads:
        if cap is not None and tested >= cap:
            break
        tested += 1
        try:
            parsed = urlparse.urlsplit(url)
            qs = dict(urlparse.parse_qsl(parsed.query, keep_blank_values=True))
            qs[param] = p
            url_mod = urlparse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlparse.urlencode(qs), parsed.fragment))
            r = session.get(strip_hash(url_mod), timeout=session.request_timeout)
            if p in (r.text or ""):
                return Finding("HIGH", "XSS", url_mod, param, f"Reflected payload: {p}")
        except Exception:
            continue
    return None

def test_dom_xss_with_js(url: str, param: str, payloads: List[str], js_cfg: Dict) -> Optional[Finding]:
    try:
        from js_renderer import js_context, render_url
    except Exception:
        return None

    headless = bool(js_cfg.get("headless", True))
    nav_timeout = int(js_cfg.get("nav_timeout_ms", 12000))
    run_timeout = int(js_cfg.get("run_timeout_ms", 4000))
    max_chars = int(js_cfg.get("max_body_chars", 200000))

    CANARY = "XSSCANARY_" + str(int(time.time() * 1000))
    console_canary = f'"><img src=x onerror=console.log("{CANARY}")>'
    test_values = list(payloads) + [console_canary]

    from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl
    try:
        with js_context(headless=headless) as browser:
            for pld in test_values:
                try:
                    parsed = urlsplit(url)
                    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
                    qs[param] = pld
                    u_mod = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(qs), parsed.fragment))
                    r = render_url(browser, u_mod, nav_timeout, run_timeout, max_chars)
                    if r.dialogs:
                        return Finding("HIGH", "XSS", u_mod, param, f"JS dialog triggered: {r.dialogs[0][:80]}")
                    if any(CANARY in m for m in r.console_messages):
                        return Finding("HIGH", "XSS", u_mod, param, "Console canary observed (onerror)")
                    if pld in (r.html or ""):
                        return Finding("HIGH", "XSS", u_mod, param, "Payload seen in rendered DOM")
                except Exception:
                    continue
    except Exception:
        return None
    return None

def test_sqli_basic(session: requests.Session, url: str, param: str, payloads: List[str], cap: Optional[int] = None) -> Optional[Finding]:
    error_signatures = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark",
        "pg_query():",
        "mysql_fetch_array()",
        "sqlstate[",
        "sqlite_error",
    ]
    try:
        baseline = (session.get(strip_hash(url), timeout=session.request_timeout).text or "")[:5000]
    except Exception:
        baseline = ""

    tested = 0
    for p in payloads:
        if cap is not None and tested >= cap:
            break
        tested += 1
        try:
            parsed = urlparse.urlsplit(url)
            qs = dict(urlparse.parse_qsl(parsed.query, keep_blank_values=True))
            qs[param] = p
            url_mod = urlparse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlparse.urlencode(qs), parsed.fragment))
            r = session.get(strip_hash(url_mod), timeout=session.request_timeout)
            body = (r.text or "")[:5000].lower()
            if any(sig in body for sig in error_signatures):
                return Finding("HIGH", "SQLi", url_mod, param, f"Error-based signature with payload: {p}")
            if baseline and abs(len(r.text or "") - len(baseline)) > 500:
                return Finding("MEDIUM", "SQLi", url_mod, param, f"Response length changed with payload: {p}")
        except Exception:
            continue
    return None

def check_security_headers(resp: requests.Response, required: List[str]) -> List[Finding]:
    f: List[Finding] = []
    headers = {k.lower(): v for k, v in resp.headers.items()}
    for h in required:
        if h.lower() not in headers:
            f.append(Finding("INFO", "Headers", resp.url, "-", f"Missing header: {h}"))
    if "strict-transport-security" not in headers and str(resp.url).startswith("https://"):
        f.append(Finding("INFO", "Headers", resp.url, "-", "No HSTS header"))
    return f


# -------------------------
# Orchestrate scan
# -------------------------
def run_scan(target: str, cfg: Dict) -> ScanResult:
    scan_start = time.time()

    s_cfg = cfg.get("scanner", {}) or {}
    excl_paths = cfg.get("exclusions", {}).get("paths", []) if cfg.get("exclusions") else []
    excl_domains = cfg.get("exclusions", {}).get("domains", []) if cfg.get("exclusions") else []
    payloads_cfg = cfg.get("payloads", {}) or {}
    required_headers = list(cfg.get("headers_required", []) or [])
    js_cfg = cfg.get("javascript", {}) or {}
    ai_cfg = cfg.get("ai", {}) or {}

    # Merge payloads via providers
    prov_static = StaticPayloadProvider(payloads_cfg)
    prov_ai = AIPayloadProvider(cfg)  # returns empty unless ai.enabled=true later
    # Build context (can be expanded later: DOM signals, target hints, etc.)
    provider_context = {
        "target": target,
        "use_js_dom_signals": bool(ai_cfg.get("context", {}).get("use_js_dom_signals", True)),
        "use_history_feedback": bool(ai_cfg.get("context", {}).get("use_history_feedback", True)),
    }
    xss_payloads = prov_static.get_xss_payloads(provider_context) + prov_ai.get_xss_payloads(provider_context)
    sqli_payloads = prov_static.get_sqli_payloads(provider_context) + prov_ai.get_sqli_payloads(provider_context)
    # Respect caps
    cap = payloads_cfg.get("max_test_payloads_per_param")
    per_param_cap = int(cap) if isinstance(cap, int) and cap > 0 else None
    if per_param_cap is not None:
        xss_payloads = xss_payloads[:per_param_cap]
        sqli_payloads = sqli_payloads[:per_param_cap]

    # Enforce same_host_only unless explicitly allowed by safety.flag
    same_host_only_cfg = bool(s_cfg.get("same_host_only", True))
    if not same_host_only_cfg and not cfg.get("safety", {}).get("allow_global_scan_flag", False):
        same_host_only_cfg = True

    session = make_session(
        user_agent=s_cfg.get("user_agent", "MiniOWASP/1.1 (+https://github.com/salmanel/owasp-tester)"),
        follow_redirects=bool(s_cfg.get("follow_redirects", True)),
        timeout=int(s_cfg.get("timeout_seconds", 15)),
        verify_ssl=bool(s_cfg.get("verify_ssl", True)),
        retries=int(s_cfg.get("retries", 1)),
        backoff_factor=float(s_cfg.get("backoff_factor", 0.25)),
    )

    proxies = s_cfg.get("proxies") or {}
    if isinstance(proxies, dict) and proxies:
        session.proxies.update(proxies)

    auth_cfg = s_cfg.get("auth", {}) or {}
    if auth_cfg.get("enabled"):
        typ = (auth_cfg.get("type") or "").lower().strip()
        creds = auth_cfg.get("credentials") or {}
        if typ == "basic":
            session.auth = (creds.get("username", ""), creds.get("password", ""))
        elif typ == "bearer":
            token = creds.get("token", "")
            if token:
                session.headers["Authorization"] = f"Bearer {token}"

    pages, forms = crawl(
        start_url=target,
        session=session,
        max_depth=int(s_cfg.get("max_depth", 2)),
        same_host_only=same_host_only_cfg,
        excludes_paths=excl_paths,
        exclude_domains=excl_domains,
        follow_redirect_hosts=bool(s_cfg.get("follow_redirect_hosts", False)),
        allowed_hosts=s_cfg.get("allowed_hosts", []),
        max_pages=int(s_cfg.get("max_pages", 100)),
        delay_ms=int(s_cfg.get("delay_ms", 250)),
        js_cfg=js_cfg,
    )

    findings: List[Finding] = []

    # Header checks for unique base URLs (no hash)
    base_urls: Set[str] = set(strip_hash(u) for u in pages)
    for u in sorted(base_urls):
        try:
            r = session.get(u, timeout=session.request_timeout)
            findings.extend(check_security_headers(r, required_headers))
        except Exception:
            pass

    js_enabled = bool(js_cfg.get("enabled", False))

    # GET param tests (XSS + SQLi) for URLs with queries
    for u in pages:
        try:
            parsed = urlparse.urlsplit(u)
            qs = dict(urlparse.parse_qsl(parsed.query, keep_blank_values=True))
            if not qs:
                continue

            # XSS
            for param in qs:
                fx = test_reflected_xss(session, u, param, xss_payloads, per_param_cap)
                if fx:
                    findings.append(fx)
                    continue
                if js_enabled:
                    fdom = test_dom_xss_with_js(u, param, xss_payloads, js_cfg)
                    if fdom:
                        findings.append(fdom)

            # SQLi
            for param in qs:
                fs = test_sqli_basic(session, u, param, sqli_payloads, per_param_cap)
                if fs:
                    findings.append(fs)
        except Exception:
            pass

    total_forms = sum(len(v) for v in forms.values())

    scan_end = time.time()
    return ScanResult(
        target=target,
        pages=pages,
        forms=forms,
        crawled_pages=len(pages),
        discovered_forms=total_forms,
        findings=findings,
        started_at=scan_start,
        finished_at=scan_end,
    )


# -------------------------
# Reporting
# -------------------------
def save_report(result: ScanResult, out_dir: str, report_cfg: Optional[Dict] = None) -> Tuple[Optional[str], Optional[str]]:
    report_cfg = report_cfg or {}
    want_json = bool(report_cfg.get("json", True))
    want_html = bool(report_cfg.get("html", True))

    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S", time.localtime(result.finished_at))
    base = os.path.join(out_dir, f"report_{ts}")

    json_path = html_path = None

    if want_json:
        json_path = base + ".json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "target": result.target,
                "pages": result.pages,
                "forms": result.forms,
                "crawled_pages": result.crawled_pages,
                "discovered_forms": result.discovered_forms,
                "findings": [asdict(x) for x in result.findings],
                "started_at": result.started_at,
                "finished_at": result.finished_at,
            }, f, indent=2)

    if want_html:
        rows = []
        for fnd in result.findings:
            rows.append(
                f"<tr><td>{html.escape(fnd.severity)}</td>"
                f"<td>{html.escape(fnd.category)}</td>"
                f"<td>{html.escape(fnd.url)}</td>"
                f"<td>{html.escape(fnd.param)}</td>"
                f"<td>{html.escape(fnd.evidence)}</td></tr>"
            )
        table = "\n".join(rows) or "<tr><td colspan='5'>No findings 🎉</td></tr>"

        forms_html_parts: List[str] = []
        if result.forms:
            for page, forms in result.forms.items():
                forms_html_parts.append(f"<h3 style='margin-top:20px'>{html.escape(page)}</h3>")
                if not forms:
                    forms_html_parts.append("<p><em>No forms.</em></p>")
                    continue
                forms_html_parts.append("<ul>")
                for fm in forms:
                    method = html.escape((fm.get('method') or 'get').upper())
                    action = html.escape(fm.get('action') or page)
                    inputs = fm.get('inputs') or {}
                    kvs = ", ".join(f"{html.escape(str(k))}" for k in inputs.keys()) if inputs else "(no inputs)"
                    forms_html_parts.append(f"<li><strong>{method}</strong> {action} &nbsp; <em>inputs:</em> {kvs}</li>")
                forms_html_parts.append("</ul>")
        else:
            forms_html_parts.append("<p><em>No forms discovered.</em></p>")
        forms_html = "\n".join(forms_html_parts)

        html_path = base + ".html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Mini OWASP Report</title>
<style>
body{{font-family:system-ui,Segoe UI,Roboto,Arial;margin:20px}}
h1{{margin:0}}small{{color:#666}}
table{{border-collapse:collapse;width:100%;margin-top:12px}}
td,th{{border:1px solid #ddd;padding:8px;font-size:14px}}
th{{background:#f2f2f2;text-align:left}}
.bad{{color:#b91c1c}} .warn{{color:#b45309}} .ok{{color:#15803d}}
h2{{margin-top:26px}}
h3{{margin:12px 0 6px 0}}
ul{{margin:6px 0 16px 18px}}
code, pre{{background:#f7f7f7; padding:2px 4px}}
</style></head>
<body>
<h1>Mini OWASP Report</h1>
<small>Target: {html.escape(result.target)} • Pages: {result.crawled_pages} • Forms: {result.discovered_forms}</small>

<h2>Findings</h2>
<table>
<thead><tr><th>Severity</th><th>Category</th><th>URL</th><th>Param</th><th>Evidence</th></tr></thead>
<tbody>
{table}
</tbody></table>

<h2>Forms (discovered)</h2>
{forms_html}

</body></html>""")

    return json_path, html_path


# -------------------------
# Pretty helpers
# -------------------------
def summary_text(result: ScanResult) -> str:
    high = sum(1 for f in result.findings if f.severity == "HIGH")
    med  = sum(1 for f in result.findings if f.severity == "MEDIUM")
    info = sum(1 for f in result.findings if f.severity in ("LOW", "INFO"))
    return f"Pages: {result.crawled_pages} | Forms: {result.discovered_forms} | HIGH: {high} | MEDIUM: {med} | INFO: {info}"
