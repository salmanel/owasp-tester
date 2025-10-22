# 🤝 Contributing Guide

Thank you for helping improve **OWASP-Tester**!

---

## 🧠 Overview
This project merges a CLI + FastAPI + React interface for a modular OWASP vulnerability scanner.
It’s designed for ethical research, security learning, and future AI-driven payload generation.

---

## 🧩 Local Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-org>/owasp-tester.git
   cd owasp-tester
   ```

2. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r packages/core/requirements.txt
   pip install -r packages/backend/requirements.txt
   cd packages/frontend && npm ci && cd -
   ```

3. **Run locally**
   ```bash
   uvicorn packages.backend.api_server:app --reload --port 8000
   cd packages/frontend && npm run dev
   ```

4. **Test**
   ```bash
   python packages/core/cli.py --url http://testphp.vulnweb.com --config packages/core/config.yaml --details
   ```

---

## 🧰 Code Style

| Area | Convention |
|------|-------------|
| Python | PEP8 + type hints + logging |
| JavaScript | ESLint + Prettier |
| Commits | `feat(core): add new feature` |
| Branches | `feat/`, `fix/`, `doc/` prefixes |
| Docstrings | Triple quotes with clear params/returns |

---

## 🔍 Validation Checklist
```bash
flake8 packages/core
mypy packages/core
cd packages/frontend && npm run lint
```
✅ Backend + Frontend both run  
✅ CLI executes without crash  
✅ Reports saved to `packages/core/reports/`

---

## 🧠 AI Provider Development
- Located in `packages/core/payloads/providers/ai_provider_stub.py`
- Add new model logic under `packages/ai/`
- Keep AI optional (disabled by default)

---

## 🧩 Pull Request Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feat/new-feature
   ```

2. Commit changes:
   ```bash
   git commit -m "feat(core): improve SQLi detection"
   ```

3. Push and open PR:
   - Describe your feature
   - Include test results or screenshots

---

## ⚖️ Conduct
- Use responsibly and legally.  
- Respect contributors’ work and document clearly.  
- No scanning unauthorized websites.

---

## 📜 License
All contributions follow the same MIT License as the main project.

---

**Maintainer:** SELY — Cybersecurity Engineer 🛡️  
Happy hacking, learning, and securing!
