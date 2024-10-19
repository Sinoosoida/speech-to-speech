from time import perf_counter
import logging
import threading
from queue import Queue
from collections import deque  # Added for efficient buffer management
import concurrent.futures
from utils.data import ImmutableDataChain

logger = logging.getLogger(__name__)

class BaseHandler:
    """
    Base class for pipeline parts. Each part of the pipeline has an input and an output queue.
    The `setup` method along with `setup_args` and `setup_kwargs` can be used to address the specific requirements of the implemented pipeline part.
    To stop a handler properly, set the stop_event and, to avoid queue deadlocks, place b"END" in the input queue.
    Objects placed in the input queue will be processed by the `process` method, and the yielded results will be placed in the output queue.
    The cleanup method handles stopping the handler, and b"END" is placed in the output queue.
    """

    def __init__(self, stop_event, queue_in, queue_out, threads=1, use_data_chain=True, setup_args=(), setup_kwargs={}):
        self.stop_event = stop_event
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.setup(*setup_args, **setup_kwargs)
        self._times = []
        self.threads = threads
        self.data_chain_input = use_data_chain
        self.data_chain_outupt = use_data_chain

        if self.threads > 1:
            # Initialization for managing the write order
            self.sequence_counter = 0  # Counter for assigning sequence numbers to requests
            self.next_write_sequence = 0  # Next sequence number that should write to the output queue
            self.write_lock = threading.Lock()  # Lock for synchronizing access to write order
            self.write_condition = threading.Condition(self.write_lock)  # Condition for notifying threads about write availability

            # Initialize thread pool for parallel processing
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)

    def setup(self, *args, **kwargs):
        pass

    def process(self, input_data):
        raise NotImplementedError

    def run(self):
        while not self.stop_event.is_set():
            input_data_chain = self.queue_in.get()

            if isinstance(input_data_chain, bytes) and input_data_chain == b"END":
                # Sentinel signal to avoid queue deadlock
                logger.debug(f"Stopping thread {self.__class__.__name__}")
                break


            if self.threads > 1:
                seq = self.sequence_counter
                self.sequence_counter += 1
                self.executor.submit(self.process_and_write, input_data_chain, seq)
            else:
                start_time = perf_counter()
                first_chunk = True

                if self.data_chain_input:
                    if not isinstance(input_data_chain, ImmutableDataChain):
                        logger.error("Incorrect input data in {self.__class__.__name__}")
                    input_data = input_data_chain.get_data()
                else:
                    input_data = input_data_chain

                for output in self.process(input_data):
                    if first_chunk:
                        logger.debug(f"{self.__class__.__name__} started output after: {self.last_time:.3f} s")
                        first_chunk = False
                    self._times.append(perf_counter() - start_time)
                    if self.last_time > self.min_time_to_debug:
                        logger.debug(f"{self.__class__.__name__}: {self.last_time:.3f} s")
                    if self.data_chain_outupt:
                        self.queue_out.put(input_data_chain.add_data(output, self.__class__.__name__))
                    else:
                        self.queue_out.put(output)
                    start_time = perf_counter()
                if self.last_time > self.min_time_to_debug:
                    logger.debug(f"{self.__class__.__name__} ended output after: {self.last_time:.3f} s")

        if self.threads > 1:
            self.executor.shutdown(wait=True)
        self.cleanup()
        self.queue_out.put(b"END")

    def process_and_write(self, input_data_chain, seq):
        start_time = perf_counter()
        buffer = deque()  # Internal buffer for storing chunks
        first_chunk = True
        writing_directly = False  # Flag to indicate if we can write directly to queue_out

        try:

            if self.data_chain_input:
                if not isinstance(input_data_chain, ImmutableDataChain):
                    logger.error("Incorrect input data in {self.__class__.__name__}")
                input_data = input_data_chain.get_data()
            else:
                input_data = input_data_chain

            for chunk in self.process(input_data):
                if first_chunk:
                    logger.debug(f"{self.__class__.__name__} started output after: {perf_counter() - start_time:.3f} s")
                    first_chunk = False

                with self.write_condition:
                    if seq == self.next_write_sequence:
                        if not writing_directly:
                            # It's our turn now
                            # Write all buffered chunks
                            while buffer:
                                if self.data_chain_outupt:
                                    self.queue_out.put(input_data_chain.add_data(buffer.popleft(), self.__class__.__name__))
                                else:
                                    self.queue_out.put(buffer.popleft())
                            writing_directly = True
                        # Write current chunk
                        if self.data_chain_outupt:
                            self.queue_out.put(input_data_chain.add_data(chunk, self.__class__.__name__))
                        else:
                            self.queue_out.put(chunk)

                    else:
                        # Not our turn yet, buffer the chunk
                        buffer.append(chunk)

            logger.debug(f"{self.__class__.__name__} finished output after: {perf_counter() - start_time:.3f} s")
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            self.stop_event.set()
            self.queue_out.put(b"END")
            return

        # Wait until it's our turn to write any remaining buffered chunks
        with self.write_condition:
            while seq != self.next_write_sequence:
                self.write_condition.wait()
            # Now it's our turn
            if not writing_directly:
                # Write any buffered chunks
                while buffer:
                    if self.data_chain_outupt:
                        self.queue_out.put(input_data_chain.add_data(buffer.popleft(), self.__class__.__name__))
                    else:
                        self.queue_out.put(buffer.popleft())
                writing_directly = True
            # Update the next sequence number
            self.next_write_sequence += 1
            # Notify other threads
            self.write_condition.notify_all()

    @property
    def last_time(self):
        return self._times[-1] if self._times else 0.0

    @property
    def min_time_to_debug(self):
        return 0.001

    def cleanup(self):
        pass
