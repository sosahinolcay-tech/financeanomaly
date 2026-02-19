"""Alert serialization for API responses."""

from typing import Any, Dict


def serialize_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare alert for JSON response."""
    return dict(alert)
