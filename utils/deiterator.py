import logging
from baseHandler import BaseHandler
from utils.data import ImmutableDataChain

logger = logging.getLogger(__name__)


class DeiteratorHandler(BaseHandler):

    def setup(self):
        pass

    def warmup(self):
        pass

    def process(self, data:ImmutableDataChain):
        iterator = data.get_data("output_audio_iterator")
        logger.debug(f"Got iterator out of text {data.get_data("llm_sentence")}")
        for chunk in iterator:
            logger.debug(f"Got a chunk out of text {data.get_data("llm_sentence")}")
            yield data.add_data(chunk, "output_audio_chunk")
        logger.debug(f"Got all chuncks of iterator out of text {data.get_data("llm_sentence")}")
