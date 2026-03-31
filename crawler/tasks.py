from utils.logging.log import Log
from utils.config.ini import Ini
from utils.config.env import Env

from . import Crawler
from .celery import app


class CrawlerTask:
    """
    Compatibility wrapper for tests.

    Historical code exposed a `CrawlerTask` class, while the current runtime
    primarily uses a Celery task function (`run_crawler`).
    """

    def __init__(self, config_file=None):
        self.config_file = config_file or Env.read("CONFIG_FILE")

    def run(self, url):
        """Run crawler synchronously and return scan report (DynamicObject)."""
        crawler = Crawler(ini=Ini(self.config_file))
        return crawler.scan(url)


@app.task(bind=True)
def run_crawler(self, url):
    Log.i(f"Starting crawler task for {url}")

    crawler = Crawler(ini=Ini(Env.read("CONFIG_FILE")))

    report = crawler.scan(url)

    if not report.is_empty() and report.webpage.url == url:
        crawler.save(self.request.id, report)

    del crawler
