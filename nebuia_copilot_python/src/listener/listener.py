import threading
import queue
from typing import Generator
from nebuia_copilot_python.src.models import BatchDocumentsResponse, StatusDocument
from nebuia_copilot_python.src.api_client import APIClient


class Listener:
    """
    A class to periodically fetch documents from an API based on a specified status.

    This class uses a background thread to fetch documents at regular intervals
    and provides a generator to access the fetched documents.

    Attributes:
        api_client (APIClient): The API client used to fetch documents.
        status (StatusDocument): The status of the documents to fetch.
        limit_documents (int): The maximum number of documents to fetch per request.
        interval (int): The interval in seconds between each fetch operation.
        thread (threading.Thread): The background thread used for fetching documents.
        stop_event (threading.Event): An event to signal the thread to stop.
        result_queue (queue.Queue[BatchDocumentsResponse]): A queue to store the fetched documents.

    Methods:
        __init__(api_client: APIClient, status: StatusDocument, interval: int, limit_documents: int):
            Initializes the Listener with the given parameters.
        start() -> None:
            Starts the background thread to fetch documents periodically.
        stop() -> None:
            Stops the background thread and waits for it to finish.
        _run() -> None:
            The target method for the background thread. Fetches documents 
            periodically and puts them in the result queue.
        results() -> Generator[BatchDocumentsResponse, None, None]:
            A generator method that yields fetched documents from the result queue.
    """

    def __init__(self, api_client: APIClient, status: StatusDocument, interval: int, limit_documents: int):
        """
        Initialize the Listener.

        Args:
            api_client (APIClient): The API client used to fetch documents.
            status (StatusDocument): The status of the documents to fetch.
            interval (int): The interval in seconds between each fetch operation.
            limit_documents (int): The maximum number of documents to fetch per request.
        """
        self.api_client: APIClient = api_client
        self.status: StatusDocument = status
        self.limit_documents: int = limit_documents
        self.interval: int = interval
        self.thread: threading.Thread = threading.Thread(
            target=self._run, daemon=True)
        self.stop_event: threading.Event = threading.Event()
        self.result_queue: queue.Queue[BatchDocumentsResponse] = queue.Queue()

    def start(self) -> None:
        """Start the background thread to fetch documents periodically."""
        self.thread.start()

    def stop(self) -> None:
        """Stop the background thread and wait for it to finish."""
        self.stop_event.set()
        self.thread.join()

    def _run(self) -> None:
        """
        The target method for the background thread.

        Continuously fetches documents at the specified interval and puts
        them in the result queue until the stop event is set.
        """
        while not self.stop_event.is_set():
            documents = self.api_client.get_documents_by_status(
                self.status, limit=self.limit_documents)
            self.result_queue.put(documents)
            self.stop_event.wait(self.interval)

    def results(self) -> Generator[BatchDocumentsResponse, None, None]:
        """
        Yield fetched documents from the result queue.

        This generator continues to yield results until the listener is stopped
        and the queue is empty.

        Yields:
            BatchDocumentsResponse: A batch of documents fetched from the API.

        Note:
            This method will block for up to 0.5 seconds when waiting for new results.
        """
        while not self.stop_event.is_set() or not self.result_queue.empty():
            try:
                yield self.result_queue.get(timeout=0.5)
            except queue.Empty:
                continue
