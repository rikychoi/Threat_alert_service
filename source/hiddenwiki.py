from .base import SourceBase

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utils.logging.log import Log
from utils.network.http import HTTP


class HiddenWikiCollector(SourceBase):
    cycle = 1440
    name = "Hidden Wiki"
    active = True

    def collect(self):
        response = HTTP.request(url="https://thehiddenwiki.com/Main_Page")

        if not response:
            Log.e("Failed to request Hidden Wiki")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a"):
            try:
                parse = urlparse(a["href"])

                # valid onion domain check routine
                if parse.scheme.startswith("http") and parse.netloc.endswith("onion"):
                    url = "{}://{}".format(parse.scheme, parse.netloc)
                    if url not in self.urls:
                        self.urls.append(url)
            except Exception:
                pass

        Log.i("{} url detected from hiddenwiki".format(len(self.urls)))