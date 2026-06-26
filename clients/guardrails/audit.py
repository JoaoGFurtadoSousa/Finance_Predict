"""Auditoria estruturada sem persistir o conteúdo sensível analisado."""

import json
import logging
from datetime import datetime, timezone


logger = logging.getLogger("investment_guardrails")


def log_guardrail(guardrail, reason, threat_type="POLICY_VIOLATION"):
    event = {
        "guardrail": guardrail,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threat_type": threat_type,
    }
    # O evento contém apenas metadados da regra; nunca inclui o payload.
    logger.warning(json.dumps(event, ensure_ascii=False), extra={"guardrail_event": event})
