import sys
import threading
import signal
from typing import Callable
from loguru import logger
from nebuia_copilot_python.src.api_client import APIClient
from nebuia_copilot_python.src.listener.manager import ThreadedListenerManager
from nebuia_copilot_python.src.models import BatchType, StatusDocument

class ListenerIntegrator:
    def __init__(self, api_client: APIClient):
        self.manager = ThreadedListenerManager(api_client)
        self.on_document_handler = None
        self.on_listener_start_handler = None
        self.on_listener_stop_handler = None
        self.on_all_complete_handler = None
        self.run_thread = None
        self._stop_event = threading.Event()

    def add_listener(self, status: StatusDocument, batch_type: BatchType, interval: int, limit_documents: int):
        self.manager.add_listener(status, batch_type, interval, limit_documents)

    def set_on_document_handler(self, handler: Callable[[StatusDocument, dict], None]):
        self.on_document_handler = handler

    def set_on_listener_start_handler(self, handler: Callable[[StatusDocument], None]):
        self.on_listener_start_handler = handler

    def set_on_listener_stop_handler(self, handler: Callable[[StatusDocument], None]):
        self.on_listener_stop_handler = handler

    def set_on_all_complete_handler(self, handler: Callable[[], None]):
        self.on_all_complete_handler = handler

    def on_document(self, status, doc):
        if self.on_document_handler:
            self.on_document_handler(status, doc)
        else:
            logger.info(f"new document from {status}: {doc}")

    def on_listener_start(self, status):
        if self.on_listener_start_handler:
            self.on_listener_start_handler(status)
        else:
            logger.info(f"listener started for status: {status}")

    def on_listener_stop(self, status):
        if self.on_listener_stop_handler:
            self.on_listener_stop_handler(status)
        else:
            logger.info(f"listener stopped for status: {status}")

    def on_all_complete(self):
        if self.on_all_complete_handler:
            self.on_all_complete_handler()
        else:
            logger.info("all listeners have completed their work")

    def setup_event_handlers(self):
        self.manager.events.on_document += self.on_document
        self.manager.events.on_listener_start += self.on_listener_start
        self.manager.events.on_listener_stop += self.on_listener_stop
        self.manager.events.on_all_complete += self.on_all_complete

    def run(self):
        self.setup_event_handlers()
        try:
            self.manager.run()
        except Exception as e:
            logger.error(f"exception in manager run: {e}")
        finally:
            self._stop_event.set()
            logger.info("listeners exited.")

    def start(self):
        if self.run_thread is None or not self.run_thread.is_alive():
            self._stop_event.clear()
            self.run_thread = threading.Thread(target=self.run)
            self.run_thread.start()
        else:
            logger.warning("listeners already running.")

    def stop(self):
        if self.run_thread and self.run_thread.is_alive():
            logger.info("stopping manager...")
            self._stop_event.set()
            self.manager.stop_all_listeners()
            self.run_thread.join(timeout=5)
        else:
            logger.warning("listeners not started or already stopped.")
