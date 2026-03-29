import json
import os
import re
from urllib.parse import urlparse

from .base import SourceBase
from utils.logging.log import Log


class ExternalToolSeedCollector(SourceBase):
    cycle = 30
    name = "External Tool Seed"
    active = False

    # Example:
    # DARKWEB_TOOL_OUTPUT=/app/data/tool_output.json
    # DARKWEB_TOOL_OUTPUT=/app/data/tool_output.txt
    OUTPUT_PATH_ENV = "DARKWEB_TOOL_OUTPUT"

    URL_PATTERN = re.compile(r'https?://[^\s"\'<>()]+')

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

    def _extract_from_any(self, data):
        found = []

        if isinstance(data, str):
            for match in self.URL_PATTERN.findall(data):
                normalized = self._normalize_url(match)
                if normalized:
                    found.append(normalized)

        elif isinstance(data, list):
            for item in data:
                found.extend(self._extract_from_any(item))

        elif isinstance(data, dict):
            for value in data.values():
                found.extend(self._extract_from_any(value))

        return found

    def collect(self):
        output_path = os.getenv(self.OUTPUT_PATH_ENV, "").strip()

        if not output_path:
            Log.e("{} is not set".format(self.OUTPUT_PATH_ENV))
            return

        if not os.path.exists(output_path):
            Log.e("Tool output file not found: {}".format(output_path))
            return

        Log.i("Reading external tool output: {}".format(output_path))

        extracted = []

        try:
            if output_path.endswith(".json"):
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                extracted = self._extract_from_any(data)
            else:
                with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                extracted = self._extract_from_any(text)
        except Exception:
            Log.e("Failed to parse tool output: {}".format(output_path))
            return

        new_count = 0
        seen = set()

        for url in extracted:
            if url in seen:
                continue
            seen.add(url)

            if url not in self.urls:
                self.urls.append(url)
                new_count += 1

        Log.i("{} url(s) detected from external tool output (new={})".format(
            len(self.urls), new_count
        ))