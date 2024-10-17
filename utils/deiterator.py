class Deiterator:

    def __init__(self, stop_event, iterator_queue, queue_out):
        self.stop_event = stop_event
        self.iterator_queue = iterator_queue
        self.queue_out = queue_out

    def run(self):
        while not self.stop_event.is_set():
            iterator = self.iterator_queue.get()
            if isinstance(iterator, bytes) and iterator == b"END":
                # Сигнализируем остановку
                break
            for chunk in iterator:
                self.queue_out.put(chunk)
        # Отправляем сигнал остановки следующему компоненту
        self.queue_out.put(b"END")
