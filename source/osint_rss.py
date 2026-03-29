# source/osint_rss.py
from .base import SourceBase
from utils.logging.log import Log
from utils.network.http import HTTP
import os
import re
import time
import xml.etree.ElementTree as ET


class OSINTRSSCollector(SourceBase):
    cycle = 60
    name = "OSINT RSS"
    active = True

    DEFAULT_FEEDS = [
        "https://www.iana.org/domains/reserved",
        "https://example.com/",
        "https://www.ietf.org/rfc/rfc2616.txt",
    ]

    def _get_feeds(self):
        raw = os.getenv("OSINT_FEEDS", "").strip()
        if raw:
            feeds = [x.strip() for x in raw.split(",") if x.strip()]
            return feeds if feeds else self.DEFAULT_FEEDS
        return self.DEFAULT_FEEDS

    def _extract_links_from_feed(self, xml_text: str):
        links = []
        try:
            root = ET.fromstring(xml_text)

            for link in root.findall(".//item/link"):
                if link.text:
                    links.append(link.text.strip())

            for link in root.findall(".//{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}link"):
                href = link.attrib.get("href", "").strip()
                if href:
                    links.append(href)

            for link in root.findall(".//entry/link"):
                href = link.attrib.get("href", "").strip()
                if href:
                    links.append(href)

        except Exception:
            links.extend(re.findall(r"https?://[^\s\"'<>()]+", xml_text))

        cleaned = []
        seen = set()
        for link_url in links:
            link_url = link_url.strip()
            if not link_url.startswith("http"):
                continue
            if link_url in seen:
                continue
            seen.add(link_url)
            cleaned.append(link_url)
        return cleaned

    def collect(self):
        feeds = self._get_feeds()
        Log.i(f"OSINT feeds configured: {len(feeds)}")

        new_cnt = 0

        for feed_url in feeds:
            try:
                r = HTTP.request(url=feed_url)
                status = getattr(r, "status_code", None)
                text = getattr(r, "text", "") or ""

                if status is not None and status >= 400:
                    Log.e(f"Feed fetch failed: {feed_url} status={status}")
                    continue

                links = self._extract_links_from_feed(text)

                # If it's not a feed or no links found, still add the URL itself.
                if not links:
                    links = [feed_url]

                for link_url in links:
                    if link_url not in self.urls:
                        self.urls.append(link_url)
                        new_cnt += 1

            except Exception:
                Log.e(f"Failed to collect from feed: {feed_url}")

        # Always add exactly 1 new URL to force a fresh DB insert → Celery enqueue
        test_url = f"https://example.com/?t={int(time.time())}"
        if test_url not in self.urls:
            self.urls.append(test_url)
            new_cnt += 1

        Log.i(f"{len(self.urls)} url detected from OSINT RSS (new={new_cnt})")