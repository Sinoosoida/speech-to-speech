import logging
from baseHandler import BaseHandler

logger = logging.getLogger(__name__)


class DeiteratorHandler(BaseHandler):

    def setup(self):
        pass

    def warmup(self):
        pass

    def process(self, iterator):
        for chunk in iterator:
            yield chunk

