import logging
from baseHandler import BaseHandler

logger = logging.getLogger(__name__)


class DeiteratorHandler(BaseHandler):
    def __init__(self):
        pass

    def warmup(self):
        pass

    def process(self, iterator):
        for chunk in iterator:
            if self._stop_event.is_set():
                break
            self.output_queue.put(chunk)

