import os
from .base import SourceBase
from utils.logging.log import Log
from utils.network.http import HTTP
from crawler.parser import parse_victim
from utils.handoff.sender import send_event_from_env


class RansomwareLiveCollector(SourceBase):
    cycle = 60
    name = "Ransomware.live"
    active = True

    BASE_URL = "https://api-pro.ransomware.live"
    RECENT_VICTIMS_API = f"{BASE_URL}/victims/recent"

    def _fetch_rows(self):
        api_key = os.environ.get("RANSOMWARE_LIVE_API_KEY", "")
        headers = {"X-API-KEY": api_key} if api_key else {}

        response = HTTP.request(url=self.RECENT_VICTIMS_API, headers=headers)

        if not response:
            Log.e("API request failed: {}".format(self.RECENT_VICTIMS_API))
            return []

        if getattr(response, "status_code", 500) != 200:
            Log.e("API bad status: {} status={}".format(
                self.RECENT_VICTIMS_API, response.status_code
            ))
            return []

        try:
            data = response.json()
            return data.get("victims", [])
        except Exception:
            Log.e("Invalid JSON from API")
            return []

    def collect(self):
        Log.i("Start collecting from ransomware.live Pro API")

        rows = self._fetch_rows()
        Log.i("{} victim(s) fetched".format(len(rows)))

        success = 0
        skipped = 0

        for row in rows:
            if not isinstance(row, dict):
                continue

            # post_url → claim_url로 매핑
            if "post_url" in row and "claim_url" not in row:
                row["claim_url"] = row["post_url"]

            event = parse_victim(row)

            # published_at을 문자열로 변환
            if event.get("published_at"):
                event["published_at"] = event["published_at"].strftime("%Y-%m-%d %H:%M:%S")

            # source_id 1 = RansomwareLive (schema.sql 기준)
            event["source_id"] = int(os.environ.get("RANSOMWARE_LIVE_SOURCE_ID", "3"))

            ok = send_event_from_env(event)
            if ok:
                success += 1
            else:
                skipped += 1

        Log.i("Done: {} sent, {} skipped (duplicate or error)".format(success, skipped))
