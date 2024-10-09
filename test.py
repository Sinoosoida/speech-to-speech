    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor
    import logging

    logger = logging.getLogger(__name__)

    class BaseHandler:
        def __init__(self, *args, **kwargs ):
            # Initialization code
            pass

        def worker_task(self, name, duration):
            print(f"Task {name} started")
            time.sleep(duration)
            print(f"Task {name} finished")
            return f"Result of task {name}"

        def thread_function(self):
            print("Thread started")
            with ThreadPoolExecutor(max_workers=30) as executor:
                futures = []
                for i in range(20):
                    future = executor.submit(self.worker_task, f"Task-{i}", 1 + i * 0.5)
                    futures.append(future)

                for future in futures:
                    result = future.result()
                    print(result)
            print("Thread finished")

        def run(self, *args, **kwargs ):
            self.thread_function()
            # Rest of your run method
#
# if __name__ == "__main__":
#     handler = BaseHandler()
#     handler_thread = threading.Thread(target=handler.run, daemon=False)
#     handler_thread.start()
#
#     # Wait for the handler thread to finish
#     handler_thread.join()
#
#     print("Main thread finished")
