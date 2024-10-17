import logging

logger = logging.getLogger(__name__)

class Deiterator:

    def __init__(self, stop_event, iterator_queue, queue_out):
        self.stop_event = stop_event
        self.iterator_queue = iterator_queue
        self.queue_out = queue_out

    def run(self):
        logger.debug("Started")
        while not self.stop_event.is_set():
            iterator = self.iterator_queue.get()
            if isinstance(iterator, bytes) and iterator == b"END":
                logger.debug("Stoped")
                break
            logger.debug("Iterating...")
            counter = 0
            for chunk in iterator:
                counter+=1
                self.queue_out.put(chunk)
            logger.debug(f"Iterating stoped, was created {counter} chunks out of one")
        # Отправляем сигнал остановки следующему компоненту
        self.queue_out.put(b"END")
