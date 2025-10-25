import React, { useEffect, useMemo, useState } from "react";
import { getScanStatus, getReportLinks } from "../api/client";
// import your UI components if you have a design system
import { Button } from "@/components/ui/button";

function useQueryScanId(): string | null {
  const params = new URLSearchParams(window.location.search);
  const q = params.get("scan");
  if (q) return q;
  // Fallback to last stored scan
  const stored = localStorage.getItem("owt:lastScanId");
  return stored || null;
}

export default function ResultsPage() {
  const scanId = useQueryScanId();
  const [status, setStatus] = useState<string>("");
  const [target, setTarget] = useState<string>("");
  const [links, setLinks] = useState<{ html_url: string; json_url: string } | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!scanId) {
      setError("No scan ID. Start a scan from Soft/Advanced mode first.");
      return;
    }
    let cancelled = false;

    async function poll() {
      try {
        const st = await getScanStatus(scanId);
        if (cancelled) return;
        setStatus(st.status || "");
        setTarget(st.url || "");
        if (["done", "completed"].includes(st.status)) {
          // Fetch report links once ready
          try {
            const r = await getReportLinks(scanId);
            if (!cancelled) {
              setLinks({ html_url: r.html_url, json_url: r.json_url });
            }
          } catch (e) {
            console.error(e);
            if (!cancelled) setError("Reports ready but links endpoint failed.");
          }
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) setError("Failed to fetch status.");
      }
    }

    // Initial + poll interval
    poll();
    const t = setInterval(poll, 3000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, [scanId]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-1">Test Results</h1>
      <p className="text-sm opacity-80 mb-4">
        {scanId ? <>Scan ID: <code>{scanId}</code> • Target: <code>{target || "…"}</code></> : "No active scan."}
      </p>

      {error && <div className="text-red-400 mb-3">{error}</div>}

      <div className="flex items-center gap-3 mb-6">
        <span>Status: <strong>{status || "…"}</strong></span>
        {links && (
          <>
            <Button asChild>
              <a href={links.html_url} target="_blank" rel="noreferrer">View HTML</a>
            </Button>
            <Button asChild>
              <a href={links.json_url} download>Download JSON</a>
            </Button>
          </>
        )}
      </div>

      {/* Your existing dashboard metrics/cards can remain below */}
      {/* Example: totals, severity buckets, and a table of findings if you render JSON */}
    </div>
  );
}
