# js_renderer.py
from dataclasses import dataclass
from typing import List, Dict, Any
from contextlib import contextmanager

from playwright.sync_api import sync_playwright, Browser

@dataclass
class JSResult:
    url: str
    html: str
    console_messages: List[str]
    dialogs: List[str]
    timed_out: bool
    links: List[str]
    forms: List[Dict[str, Any]]

@contextmanager
def js_context(headless: bool = True):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    try:
        yield browser
    finally:
        try:
            browser.close()
        except Exception:
            pass
        pw.stop()

# RAW triple-quoted JS to avoid Python escaping issues
_JS_COLLECTOR: str = r"""
(() => {
  const abs = (u) => {
    try { return new URL(u, location.href).href; } catch(e) { return null; }
  };

  // 1) Classic anchors
  const hrefs = Array.from(document.querySelectorAll('a[href]'))
    .map(a => a.getAttribute('href'))
    .filter(Boolean);

  // 2) SPA routes: routerLink / ng-reflect-router-link (Angular)
  const routerLinks = Array.from(document.querySelectorAll('[routerLink], [ng-reflect-router-link]'))
    .flatMap(el => {
      let v = el.getAttribute('routerLink') || el.getAttribute('ng-reflect-router-link') || "";
      if (Array.isArray(v)) v = v.join('');
      if (typeof v !== 'string') v = String(v || '');
      return [v];
    })
    .filter(Boolean);

  // 3) Hash links (e.g., "#/search")
  const hashHrefs = Array.from(document.querySelectorAll('a[href^="#"]'))
    .map(a => a.getAttribute('href'))
    .filter(Boolean);

  // Resolve to absolute URLs
  const linkSet = new Set();
  for (const h of hrefs) {
    const u = abs(h);
    if (u) linkSet.add(u);
  }
  for (const r of routerLinks) {
    let u = r;
    if (r.startsWith('#')) {
      const base = location.href.split('#')[0];
      u = base + r;
    } else {
      const absu = abs(r);
      if (absu) {
        u = absu;
      } else {
        const guess = abs('/' + r.replace(/^\/+/, ''));
        if (guess) u = guess;
      }
    }
    if (u) linkSet.add(u);
  }
  for (const hh of hashHrefs) {
    const base = location.href.split('#')[0];
    linkSet.add(base + hh);
  }

  // --------------------------
  // Forms (Angular-friendly)
  // --------------------------
  // Build a quick label -> input map using [for=id]
  const labelFor = {};
  Array.from(document.querySelectorAll('label[for]')).forEach(l => {
    const id = l.getAttribute('for');
    const text = (l.textContent || '').trim();
    if (id) labelFor[id] = text;
  });

  // Helper: pick best "name" for a control
  const bestName = (el, idx) => {
    const n = el.getAttribute('name')
      || el.getAttribute('formcontrolname')
      || el.getAttribute('ng-reflect-name')
      || el.getAttribute('ng-reflect-form-control-name')
      || el.getAttribute('id')
      || el.getAttribute('aria-label')
      || el.getAttribute('placeholder');
    if (n) return String(n);

    // If there's a label[for] pointing to this id, use it
    const idAttr = el.getAttribute('id');
    if (idAttr && labelFor[idAttr]) return labelFor[idAttr];

    // Fallback: synthesize a stable-ish key
    const t = (el.getAttribute('type') || el.tagName || 'input').toLowerCase();
    return `${t}_${idx}`;
  };

  // Extract value for selects, inputs, textareas
  const pickValue = (el) => {
    const tag = el.tagName.toLowerCase();
    if (tag === 'select') {
      const opt = el.querySelector('option[selected]') || el.querySelector('option');
      if (opt) return opt.getAttribute('value') || opt.textContent || '';
      return '';
    }
    if (tag === 'input' || tag === 'textarea') {
      // For checkboxes/radios, expose "checked" as value-ish
      const type = (el.getAttribute('type') || '').toLowerCase();
      if (['checkbox','radio'].includes(type)) {
        return el.checked ? (el.value || 'on') : '';
      }
      return el.value || el.getAttribute('value') || '';
    }
    return '';
  };

  // Collect <form>…<input>… plus a pseudo-form fallback when page uses reactive forms without <form>
  const outForms = [];

  // Real forms
  Array.from(document.querySelectorAll('form')).forEach(f => {
    const action = f.getAttribute('action') || location.href;
    const method = (f.getAttribute('method') || 'get').toLowerCase();
    const inputs = {};
    const els = f.querySelectorAll('input, textarea, select');
    let idx = 0;
    els.forEach(el => {
      const key = bestName(el, idx++);
      if (!key) return;
      inputs[key] = pickValue(el);
    });
    outForms.push({ action: abs(action) || action, method, inputs });
  });

  // Pseudo-form if there was no <form> tag but the page shows input controls
  if (outForms.length === 0) {
    const inputs = {};
    const els = document.querySelectorAll('input, textarea, select');
    let idx = 0;
    els.forEach(el => {
      // Skip obviously decorative or hidden fields
      const type = (el.getAttribute('type') || '').toLowerCase();
      if (type === 'hidden') return;
      const rect = el.getBoundingClientRect();
      if (rect && (rect.width === 0 || rect.height === 0)) return;

      const key = bestName(el, idx++);
      if (!key) return;
      inputs[key] = pickValue(el);
    });
    const hasInputs = Object.keys(inputs).length > 0;
    if (hasInputs) {
      outForms.push({ action: location.href, method: 'get', inputs });
    }
  }

  return { links: Array.from(linkSet), forms: outForms };
})()
"""

def _collect_dom(page) -> Dict[str, Any]:
    """
    Execute the JS collector inside the page:
      - Anchors and SPA router links (absolute)
      - Forms with Angular-friendly input discovery
      - Pseudo-form if no <form> present but inputs exist
    """
    return page.evaluate(_JS_COLLECTOR)

def render_url(browser: Browser, url: str, nav_timeout_ms: int, run_timeout_ms: int, max_body_chars: int) -> JSResult:
    page = browser.new_page()
    console_logs: List[str] = []
    dialogs: List[str] = []
    timed_out = False

    def on_console(msg):
        try:
            console_logs.append(msg.text())
        except Exception:
            pass

    def on_dialog(dialog):
        try:
            dialogs.append(dialog.message)
            dialog.dismiss()
        except Exception:
            pass

    page.on("console", on_console)
    page.on("dialog", on_dialog)

    links: List[str] = []
    forms: List[Dict[str, Any]] = []
    try:
        page.set_default_navigation_timeout(nav_timeout_ms)
        # Load page then give Angular some extra time to render
        page.goto(url, wait_until="load")
        page.wait_for_load_state("networkidle", timeout=nav_timeout_ms)
        page.wait_for_timeout(run_timeout_ms)
        html = page.content()
        info = _collect_dom(page)
        links = info.get("links") or []
        forms = info.get("forms") or []
    except Exception:
        timed_out = True
        try:
            html = page.content()
        except Exception:
            html = ""
    finally:
        try:
            page.close()
        except Exception:
            pass

    if len(html) > max_body_chars:
        html = html[:max_body_chars]
    return JSResult(
        url=url,
        html=html,
        console_messages=console_logs,
        dialogs=dialogs,
        timed_out=timed_out,
        links=links,
        forms=forms,
    )
