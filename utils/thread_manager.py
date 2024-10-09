import threading


class ThreadManager:
    """
    Manages multiple threads used to execute given handler tasks.
    """

    def __init__(self, handlers):
        self.handlers = handlers
        self.threads = []

    def start(self):
        print("start")
        for handler in self.handlers:
            print(f"starting{handler}")
            thread = threading.Thread(target=handler.run)
            self.threads.append(thread)
            thread.start()

    def stop(self):
        print("smth")
        for handler in self.handlers:
            handler.stop_event.set()
        for thread in self.threads:
            thread.join()
