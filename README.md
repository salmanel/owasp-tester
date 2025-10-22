# 🛡️ OWASP-Tester

**A modular, AI-ready OWASP vulnerability scanner — CLI + Web UI + FastAPI backend.**
Built by cybersecurity engineers for research, automation, and collaborative development.

---

## 🚀 Overview

OWASP-Tester combines a Python-based scanner (XSS, SQLi, headers)
with a FastAPI backend and a React (Vite) frontend for report visualization.

It’s designed to:
- Perform local web vulnerability scans.
- Detect common OWASP Top-10 flaws (currently XSS + SQLi + header checks).
- Serve reports via API and browser interface.
- Later: integrate deep learning for adaptive payload generation.

---

## 🧩 Repository Structure

```
owasp-tester/
├── README.md
├── CONTRIBUTING.md
├── docker-compose.yml
├── third_party/
│   ├── xss-payload-list/
│   └── sql-injection-payload-list/
├── packages/
│   ├── core/                      # Scanner engine + CLI
│   │   ├── cli.py
│   │   ├── wvscanner_core.py
│   │   ├── js_renderer.py
│   │   ├── config.yaml
│   │   └── payloads/providers/
│   │       ├── interface.py
│   │       ├── static_provider.py
│   │       └── ai_provider_stub.py
│   ├── backend/                   # FastAPI server
│   │   ├── api_server.py
│   │   └── requirements.txt
│   └── frontend/                  # React web interface
│       ├── package.json
│       └── src/
│           ├── api/client.ts
│           └── components/ScanPanel.tsx
└── tools/
    ├── run_local_scan.sh
    └── run_frontend.sh
```

---

## ⚙️ Quick Start

### 1️⃣ Requirements
- **Python** ≥ 3.10
- **Node.js** ≥ 18 + npm
- *(Optional)* Playwright (for JS rendering)
- *(Optional)* Docker (for test labs)

### 2️⃣ Setup
```bash
git clone https://github.com/<yourname>/owasp-tester.git
cd owasp-tester
python3 -m venv .venv
source .venv/bin/activate
pip install -r packages/core/requirements.txt
pip install -r packages/backend/requirements.txt
cd packages/frontend && npm ci && cd -
```

### 3️⃣ Run the stack
Backend:
```bash
uvicorn packages.backend.api_server:app --host 0.0.0.0 --port 8000 --reload
```
Frontend:
```bash
cd packages/frontend && npm run dev
# open http://localhost:5173
```
CLI:
```bash
python packages/core/cli.py --url http://testphp.vulnweb.com --config packages/core/config.yaml --details
```

---

## 📊 Reports
Reports are saved under:
```
packages/core/reports/
├── report_YYYYMMDD-HHMMSS.json
└── report_YYYYMMDD-HHMMSS.html
```
Open the HTML file in your browser to view findings.

---

## 🧰 Payloads
Payload lists come from third-party repos:
- [payloadbox/xss-payload-list](https://github.com/payloadbox/xss-payload-list)
- [payloadbox/sql-injection-payload-list](https://github.com/payloadbox/sql-injection-payload-list)

Configured in `packages/core/config.yaml`:
```yaml
payloads:
  xss_files:
    - "../../third_party/xss-payload-list/Intruder/xss-payload-list.txt"
  sqli_files:
    - "../../third_party/sql-injection-payload-list/Intruder/detect"
    - "../../third_party/sql-injection-payload-list/Intruder/exploit"
    - "../../third_party/sql-injection-payload-list/Intruder/payloads-sql-blind"
  max_test_payloads_per_param: 150
```

---

## 🧪 Safe Targets
| Target | Description | Command |
|--------|--------------|----------|
| VulnWeb | Public demo site | `http://testphp.vulnweb.com` |
| DVWA | OWASP training app | `docker run -d -p 8081:80 vulnerables/web-dvwa` |
| SQLi-Labs | SQL injection tests | `docker run -d -p 8082:80 neuralegion/sqli-lab` |
| bWAPP | Multi-vuln lab | `docker run -d -p 8080:80 raesene/bwapp` |

---

## 🧠 AI Integration (Future)
- The core supports an `ai_provider_stub.py` for ML-based payload generation.
- Future versions will include adaptive payloads and feedback-based learning.

---

## ⚖️ Legal & Ethical Use
Use only on **authorized systems**.  
Unauthorized scanning is illegal and unethical.  
This tool is for research and educational testing.

---

## 👩‍💻 Maintainer
**SELY** — Cybersecurity Engineer & Researcher  
GitHub: [@salmanel](https://github.com/salmanel)

---

## 📜 License
```
MIT License © 2025
```

---

## 🤝 Contributing
Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting pull requests.
