class GuardrailViolation(ValueError):
    """Erro controlado usado quando uma proteção impede o fluxo."""

    def __init__(self, guardrail, reason, message, details=None):
        self.guardrail = guardrail
        self.reason = reason
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def as_dict(self):
        result = {
            "guardrail": self.guardrail,
            "code": self.reason,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result
