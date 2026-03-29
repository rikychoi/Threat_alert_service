"""
Define base class for formatting source collector.

Developed by Namjun Kim (bunseokbot@gmail.com)
"""

from uuid import uuid4

from crawler.tasks import run_crawler

from database.session import Session
from database.engine import Engine
from database.models import Domain

from utils.logging.log import Log
from utils.config.ini import Ini
from utils.config.env import Env


class SourceBase(object):
    """Base source object class format."""
    ini = Ini(Env.read('CONFIG_FILE'))
    active = True  # collector status

    def __init__(self):
        # Use instance-level URL queue to avoid cross-source contamination.
        self.urls = []

    def collect(self):
        """
        Run user custom method.
        :return:
        """
        pass

    def save(self):
        """
        Save domain on database and request crawling.
        :return: None
        """
        engine = Engine.create(self.ini)

        with Session(engine=engine) as session:
            pending_urls = list(self.urls)

            for url in pending_urls:
                task_id = uuid4().hex

                try:
                    # add url into database
                    session.add(Domain(uuid=task_id, url=url))
                    session.commit()

                    task = run_crawler.apply_async(args=(url,), task_id=task_id)
                    Log.i("Crawler issued a new task id {} at {}".format(
                        task.task_id, url
                    ))
                except Exception:
                    session.rollback()
                    Log.d("This {} url already saved into database.".format(url))
                finally:
                    if url in self.urls:
                        self.urls.remove(url)

        engine.dispose()