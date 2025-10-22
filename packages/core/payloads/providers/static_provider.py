from pathlib import Path
from typing import List, Dict
from .interface import PayloadProvider

class StaticPayloadProvider(PayloadProvider):
    """Reads payloads from config and external text files (xss_files/sqli_files)."""
    def __init__(self, payload_cfg: Dict):
        self.cfg = payload_cfg or {}

    def _read_files(self, file_list: List[str]) -> List[str]:
        out: List[str] = []
        for f in file_list or []:
            p = Path(f)
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    s = line.strip()
                    if s and not s.startswith("#"):
                        out.append(s)
        # dedupe preserving order
        seen = set(); dedup = []
        for x in out:
            if x not in seen:
                seen.add(x); dedup.append(x)
        return dedup

    def get_xss_payloads(self, context: Dict) -> List[str]:
        inline = list(self.cfg.get("xss_reflected", []) or [])
        files  = self._read_files(self.cfg.get("xss_files") or [])
        return inline + files

    def get_sqli_payloads(self, context: Dict) -> List[str]:
        inline = list(self.cfg.get("sqli_basic", []) or [])
        files  = self._read_files(self.cfg.get("sqli_files") or [])
        return inline + files
