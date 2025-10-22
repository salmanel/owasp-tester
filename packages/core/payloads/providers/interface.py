from typing import List, Dict

class PayloadProvider:
    """Abstract base class for any payload provider (static or AI)."""
    def get_xss_payloads(self, context: Dict) -> List[str]:
        raise NotImplementedError

    def get_sqli_payloads(self, context: Dict) -> List[str]:
        raise NotImplementedError
