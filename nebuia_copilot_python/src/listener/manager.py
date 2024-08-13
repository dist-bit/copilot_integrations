import signal
import time
import threading
from typing import Dict
from loguru import logger
from events import Events
from nebuia_copilot_python.src.api_client import APIClient
from nebuia_copilot_python.src.models import BatchType, StatusDocument

class ListenerEvents(Events):
    __events__ = ('on_document', 'on_error', 'on_complete')

class ThreadedEventBasedListener:
    def __init__(self, api_client: APIClient, status: StatusDocument, batchType: BatchType, interval: int, limit_documents: int):
        self.api_client = api_client
        self.status = status
        self.batch_type = batchType
        self.interval = interval
        self.limit_documents = limit_documents
        self.stop_flag = False
        self.thread = None
        self.events = ListenerEvents()

    def fetch_documents(self):
        documents = self.api_client.get_documents_by_status_and_batch(
            status=self.status,
            batch_type=self.batch_type,
            limit=self.limit_documents
        )
        return documents

    def run(self):
        while not self.stop_flag:
            try:
                documents = self.fetch_documents()
                for doc in documents.documents:
                    self.events.on_document(self.status, doc)
            except Exception as e:
                self.events.on_error(str(e))
            time.sleep(self.interval)
        self.events.on_complete(self.status)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        self.stop_flag = True
        if self.thread and self.thread.is_alive():
            self.thread.join()

class ManagerEvents(Events):
    __events__ = ('on_document', 'on_listener_start', 'on_listener_stop', 'on_all_complete')

class ThreadedListenerManager:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.listeners: Dict[StatusDocument, ThreadedEventBasedListener] = {}
        self.events = ManagerEvents()
        self.stop_flag = threading.Event()
        signal.signal(signal.SIGINT, self._signal_handler)

    def add_listener(self, status: StatusDocument, batchType: BatchType, interval: int, limit_documents: int) -> ThreadedEventBasedListener:
        listener = ThreadedEventBasedListener(
            self.api_client, status=status, batchType=batchType, interval=interval,
            limit_documents=limit_documents
        )
        self.listeners[status] = listener
        listener.events.on_document += self.on_listener_document
        listener.events.on_error += lambda e: logger.error(f"Listener error: {e}")
        listener.events.on_complete += lambda s: self.events.on_listener_stop(s)
        return listener

    def on_listener_document(self, status, doc):
        self.events.on_document(status, doc)

    def start_all_listeners(self):
        for status, listener in self.listeners.items():
            listener.start()
            self.events.on_listener_start(status)

    def stop_all_listeners(self):
        for status, listener in self.listeners.items():
            listener.stop()
            self.events.on_listener_stop(status)

    def run(self):
        self.start_all_listeners()
        try:
            while not self.stop_flag.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("keyboard interrupt received.")
        finally:
            self.stop_all_listeners()
            self.events.on_all_complete()

    def _signal_handler(self, signum, frame):
        logger.info(f"initiating shutdown listeners...")
        self.stop_flag.set()