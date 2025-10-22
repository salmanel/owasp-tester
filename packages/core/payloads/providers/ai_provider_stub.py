from typing import List, Dict
from .interface import PayloadProvider

class AIPayloadProvider(PayloadProvider):
    """
    Placeholder AI provider (returns empty lists until ai.enabled is true
    and a real provider is wired).
    """
    def __init__(self, root_cfg: Dict):
        self.root_cfg = root_cfg or {}

    def _enabled(self) -> bool:
        ai = self.root_cfg.get("ai", {}) or {}
        return bool(ai.get("enabled"))

    def get_xss_payloads(self, context: Dict) -> List[str]:
        if not self._enabled():
            return []
        # Later: call local/remote model to generate payloads using 'context'
        return []

    def get_sqli_payloads(self, context: Dict) -> List[str]:
        if not self._enabled():
            return []
        return []
