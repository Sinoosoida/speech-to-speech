import logging
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class InterruptionManagerHandler:
    def __init__(self, stop_event, interruption_request_queue):
        self.stop_event = stop_event
        self.interruption_request_queue = interruption_request_queue

    def run(self):
        logger.info("Interruption Manager started.")
        while not self.stop_event.is_set():
            try:
                interruption_request = self.interruption_request_queue.get(timeout=0.05)
                if interruption_request is not None:
                    logger.info(f"Processing interruption request: {interruption_request}")

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error while handling interruption: {e}")

        logger.info("Interruption Manager stopped.")
