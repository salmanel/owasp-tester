export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function startScan(url: string) {
  const res = await fetch(`${API_BASE}/scan/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error("Failed to start scan");
  return res.json() as Promise<{ scan_id: string; status: string; target: string }>;
}

export async function getScanStatus(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}/status`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json() as Promise<{ id: string; url: string; status: string }>;
}

export async function getReportLinks(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}/links`);
  if (!res.ok) throw new Error("Failed to fetch report links");
  return res.json() as Promise<{ scan_id: string; html_url: string; json_url: string }>;
}
