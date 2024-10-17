class ProcessIterator:
    def __init__(self, manager):
        self.queue = manager.Queue()
        self._sentinel = '<END_OF_ITERATOR>'

    def put(self, item):
        self.queue.put(item)

    def close(self):
        self.queue.put(self._sentinel)

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item == self._sentinel:
            raise StopIteration
        return item