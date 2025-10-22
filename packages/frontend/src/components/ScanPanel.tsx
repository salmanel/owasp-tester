import React from "react";
import {
  startScan,
  openStream,
  getStatus,
  fetchReportHtml,
  getReportLinks,
  resolveApiUrl,
} from "../api/client";

export default function ScanPanel() {
  const [url, setUrl] = React.useState("http://localhost:3000");
  const [scanId, setScanId] = React.useState<string | null>(null);
  const [status, setStatus] = React.useState<any>(null);
  const [logs, setLogs] = React.useState<string[]>([]);
  const [reportHtml, setReportHtml] = React.useState<string | null>(null);
  const [reportLinks, setReportLinks] = React.useState<{ html_url: string; json_url: string } | null>(null);

  async function onStart() {
    setLogs([]);
    setReportHtml(null);
    setReportLinks(null);

    const { scan_id } = await startScan(url);
    setScanId(scan_id);

    // initial status
    setStatus(await getStatus(scan_id));

    // live stream
    const close = openStream(
      scan_id,
      (st) => setStatus((prev: any) => ({ ...(prev || {}), ...(st || {}) })),
      (line) => setLogs((prev) => [...prev, line])
    );

    // poll until finish to fetch links + embed HTML
    const timer = setInterval(async () => {
      const s = await getStatus(scan_id);
      setStatus(s);
      if (s.state !== "running") {
        clearInterval(timer);
        close();
        try {
          const html = await fetchReportHtml(scan_id);
          setReportHtml(html);
        } catch {}
        try {
          const links = await getReportLinks(scan_id);
          setReportLinks(links);
        } catch {}
      }
    }, 1200);
  }

  const viewHtmlHref = reportLinks ? resolveApiUrl(reportLinks.html_url) : "#";
  const downloadJsonHref = reportLinks ? resolveApiUrl(reportLinks.json_url) : "#";

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Mini OWASP Scanner</h1>

      <div className="flex gap-2 mb-4">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Target URL (e.g., http://localhost:8081)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button className="bg-black text-white px-4 py-2 rounded" onClick={onStart}>
          Start Scan
        </button>
      </div>

      {status && (
        <div className="mb-4">
          <div className="text-sm text-gray-600">Scan ID: {scanId}</div>
          <div className="mt-1">
            State: <b>{status.state}</b> • Progress: {status.progress}%
          </div>
          <div className="text-sm">
            Pages: {status.pages} • Forms: {status.forms} • Findings: {status.findings}
          </div>
          {status.message && <div className="text-red-600 text-sm mt-1">Error: {status.message}</div>}
        </div>
      )}

      {reportLinks && (
        <div className="mb-4 flex gap-3">
          <a
            className="inline-flex items-center bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
            href={viewHtmlHref}
            target="_blank"
            rel="noreferrer"
          >
            View HTML Report ↗
          </a>
          <a
            className="inline-flex items-center bg-gray-800 text-white px-3 py-2 rounded hover:bg-gray-900"
            href={downloadJsonHref}
            target="_blank"
            rel="noreferrer"
          >
            Download JSON
          </a>
        </div>
      )}

      <div className="mb-4">
        <h2 className="font-medium mb-2">Live log</h2>
        <pre className="bg-gray-100 p-3 rounded h-40 overflow-auto text-sm">
{logs.join("\n")}
        </pre>
      </div>

      {reportHtml && (
        <div className="mb-10">
          <h2 className="font-medium mb-2">Report (HTML Preview)</h2>
          <iframe title="report" className="w-full h-[600px] border rounded" srcDoc={reportHtml} />
        </div>
      )}
    </div>
  );
}
