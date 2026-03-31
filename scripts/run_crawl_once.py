import argparse
import json

from crawler import Crawler
from utils.config.ini import Ini
from utils.config.env import Env
from utils.handoff import build_crawl_event, send_event_from_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--config", default=None, help="Path to ini config; defaults to CONFIG_FILE env")
    parser.add_argument("--send", action="store_true", help="Send event to backend via BACKEND_INGEST_URL")
    args = parser.parse_args()

    config_path = args.config or Env.read("CONFIG_FILE") or "files/config.ini"
    ini = Ini(config_path)

    crawler = Crawler(ini=ini)
    result = crawler.scan(args.url)

    # Build DTO for backend handoff
    event = build_crawl_event(result)
    print(json.dumps(event, ensure_ascii=False))

    if args.send:
        ok = send_event_from_env(event)
        if not ok:
            raise SystemExit(2)


if __name__ == "__main__":
    main()

