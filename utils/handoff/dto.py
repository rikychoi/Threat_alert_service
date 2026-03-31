from datetime import datetime, timezone


def build_crawl_event(scan_obj):
    """
    Normalize crawler output into a JSON-serializable DTO for backend handoff.

    This function is intentionally conservative (minimal fields, masked PII).
    """
    meta = getattr(scan_obj, "meta", {}) or {}

    webpage = getattr(scan_obj, "webpage", None)
    port = getattr(scan_obj, "port", None)
    pii = getattr(scan_obj, "pii", None)

    event = {
        "event_type": "darklight.crawl",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "meta": {
            "url": meta.get("url"),
            "domain": meta.get("domain"),
            "status": meta.get("status"),
            "error_type": meta.get("error_type"),
            "error_message": meta.get("error_message"),
        },
        "webpage": None,
        "portscan": port,
        "pii": pii,
    }

    if webpage is not None:
        event["webpage"] = {
            "url": getattr(webpage, "url", None),
            "domain": getattr(webpage, "domain", None),
            "title": getattr(webpage, "title", None),
            "language": getattr(webpage, "language", None),
        }

    return event

