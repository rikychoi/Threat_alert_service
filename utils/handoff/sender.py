import os
from typing import Optional

import requests

from utils.logging.log import Log


def send_event(event: dict, endpoint_url: str, api_key: Optional[str] = None, timeout: int = 15) -> bool:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.post(endpoint_url, json=event, headers=headers, timeout=timeout)
        if 200 <= r.status_code < 300:
            return True
        Log.e(f"Backend responded {r.status_code}: {r.text}")
        return False
    except Exception as e:
        Log.e(f"Failed to send event: {e}")
        return False


def send_event_from_env(event: dict) -> bool:
    endpoint = os.environ.get("BACKEND_INGEST_URL")
    if not endpoint:
        Log.e("BACKEND_INGEST_URL is not set; skipping send.")
        return False
    api_key = os.environ.get("BACKEND_INGEST_API_KEY")
    return send_event(event, endpoint_url=endpoint, api_key=api_key)

