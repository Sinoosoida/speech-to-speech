import logging

logger = logging.getLogger(__name__)

class InterruptionManagerHandler:
    def __init__(self, stop_event, is_speaking_event):
        self.stop_event = stop_event
        self.is_speaking_event = is_speaking_event

    def run(self):
        while not self.stop_event.is_set():
            event_is_set = self.is_speaking_event.wait(timeout=0.1)
            if self.stop_event.is_set():
                break
            if event_is_set:
                logger.debug("Пользователь начал говорить достаточно долго.")
                self.is_speaking_event.clear()
                logger.debug("Событие is_speaking_event сброшено.")
