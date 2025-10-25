import React, { useState } from "react";
import { startScan } from "../api/client";

// If you already have your own Button component, import it.
// Otherwise replace with a plain <button>.
import { Button } from "@/components/ui/button";

// If you use react-router:
import { useNavigate } from "react-router-dom";

export default function ScanPanel() {
  const [targetUrl, setTargetUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  async function handleRun() {
    if (!targetUrl) return;
    setSubmitting(true);
    try {
      const res = await startScan(targetUrl);
      const scanId = res.scan_id;
      // Remember last scan for the Results page
      localStorage.setItem("owt:lastScanId", scanId);
      // Go to results so user can watch status & export
      navigate(`/results?scan=${encodeURIComponent(scanId)}`);
    } catch (e) {
      console.error(e);
      alert("Failed to start scan");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Soft Mode</h2>
      <div className="mb-3">
        <label className="block text-sm mb-1">Target URL</label>
        <input
          className="w-full border rounded px-2 py-1 bg-transparent"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          placeholder="http://testphp.vulnweb.com"
        />
      </div>

      <Button onClick={handleRun} disabled={submitting || !targetUrl}>
        {submitting ? "Starting…" : "Run Test"}
      </Button>
    </div>
  );
}
