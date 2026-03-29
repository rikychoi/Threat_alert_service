from urllib.parse import urlparse

from .base import SourceBase

from utils.logging.log import Log
from utils.network.http import HTTP


class RansomwareLiveCollector(SourceBase):
    cycle = 60
    name = "Ransomware.live"
    active = True

    BASE_URL = "https://api.ransomware.live/v2"
    RECENT_VICTIMS_API = f"{BASE_URL}/recentvictims"
    RECENT_ATTACKS_API = f"{BASE_URL}/recentcyberattacks"

    def _normalize_url(self, raw_url):
        if not raw_url or not isinstance(raw_url, str):
            return None

        raw_url = raw_url.strip()
        if not raw_url.startswith(("http://", "https://")):
            return None

        try:
            parsed = urlparse(raw_url)
            if not parsed.scheme or not parsed.netloc:
                return None
            return "{}://{}".format(parsed.scheme, parsed.netloc)
        except Exception:
            return None

    def _extract_urls_from_value(self, value):
        extracted = []

        if isinstance(value, str):
            url = self._normalize_url(value)
            if url:
                extracted.append(url)

        elif isinstance(value, list):
            for item in value:
                extracted.extend(self._extract_urls_from_value(item))

        elif isinstance(value, dict):
            for nested_value in value.values():
                extracted.extend(self._extract_urls_from_value(nested_value))

        return extracted

    def _extract_candidate_urls(self, row):
        candidates = []

        preferred_fields = [
            "url",
            "website",
            "link",
            "press",
            "source",
            "post_url",
            "discovery_url",
        ]

        for field in preferred_fields:
            if field in row:
                candidates.extend(self._extract_urls_from_value(row.get(field)))

        # fallback: scan all values once if preferred fields do not produce URLs
        if not candidates:
            for value in row.values():
                candidates.extend(self._extract_urls_from_value(value))

        result = []
        seen = set()

        for url in candidates:
            if url not in seen:
                seen.add(url)
                result.append(url)

        return result

    def _fetch_rows(self, url):
        response = HTTP.request(url=url)

        if not response:
            Log.e("API request failed: {}".format(url))
            return []

        if getattr(response, "status_code", 500) != 200:
            Log.e("API request bad status: {} status={}".format(
                url, response.status_code
            ))
            return []

        try:
            data = response.json()
        except Exception:
            Log.e("Invalid JSON from API: {}".format(url))
            return []

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ("data", "items", "results"):
                if isinstance(data.get(key), list):
                    return data[key]

        return []

    def _collect_endpoint(self, endpoint_url):
        rows = self._fetch_rows(endpoint_url)
        new_count = 0

        Log.i("{} row(s) fetched from {}".format(len(rows), endpoint_url))

        for row in rows:
            if not isinstance(row, dict):
                continue

            urls = self._extract_candidate_urls(row)

            for url in urls:
                if url not in self.urls:
                    self.urls.append(url)
                    new_count += 1

        return new_count

    def collect(self):
        Log.i("Start collecting from ransomware.live API")

        total_new = 0
        total_new += self._collect_endpoint(self.RECENT_VICTIMS_API)
        total_new += self._collect_endpoint(self.RECENT_ATTACKS_API)

        Log.i("{} url(s) detected from ransomware.live (new={})".format(
            len(self.urls), total_new
        ))