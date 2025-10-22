const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export type ScanStatus = {
  scan_id: string;
  target: string;
  started_at: number;
  finished_at?: number | null;
  state: "running" | "finished" | "error";
  progress: number;
  message: string;
  pages: number;
  forms: number;
  findings: number;
  json_path?: string | null;
  html_path?: string | null;
};

export async function startScan(url: string, configPath = "packages/core/config.yaml", details = true) {
  const res = await fetch(`${API_BASE}/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, config_path: configPath, details }),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { scan_id: string };
}

export async function getStatus(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}/status`);
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as ScanStatus;
}

export function openStream(scanId: string, onStatus: (st: Partial<ScanStatus>) => void, onLog: (line: string) => void) {
  const es = new EventSource(`${API_BASE}/scan/${scanId}/stream`);
  es.addEventListener("status", (e: MessageEvent) => {
    try { onStatus(JSON.parse(e.data)); } catch {}
  });
  es.addEventListener("log", (e: MessageEvent) => onLog(e.data));
  es.onerror = () => {};
  return () => es.close();
}

export async function fetchReportHtml(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}/report.html`);
  if (!res.ok) throw new Error(await res.text());
  return await res.text();
}

export async function getReportLinks(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}/report.links`);
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { html_url: string; json_url: string };
}

export function resolveApiUrl(path: string) {
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path}`;
}
