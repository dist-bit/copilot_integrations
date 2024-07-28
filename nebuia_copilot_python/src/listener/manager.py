from typing import List
from nebuia_copilot_python.src.api_client import APIClient
from nebuia_copilot_python.src.models import StatusDocument
from nebuia_copilot_python.src.listener.listener import Listener


class ListenerManager:
    """
    Manages multiple Listener instances for fetching documents from an API.

    This class provides functionality to create, start, and manage multiple Listener
    objects, each responsible for fetching documents with a specific status at
    regular intervals.

    Attributes:
        api_client (APIClient): The API client used by all managed Listeners.
        listeners (List[Listener]): A list of all active Listener instances.

    Methods:
        __init__(api_client: APIClient):
            Initializes the ListenerManager with an API client.
        
        add_listener(status: StatusDocument, interval: int, limit_documents: int) -> Listener:
            Creates, starts, and adds a new Listener to the manager.
        
        stop_all_listeners():
            Stops all active Listeners and clears the list.
    """

    def __init__(self, api_client: APIClient):
        """
        Initialize the ListenerManager.

        Args:
            api_client (APIClient): The API client to be used by all managed Listeners.
        """
        self.api_client = api_client
        self.listeners: List[Listener] = []

    def add_listener(self, status: StatusDocument, interval: int, limit_documents: int) -> Listener:
        """
        Create, start, and add a new Listener to the manager.

        This method creates a new Listener instance with the specified parameters,
        starts it, adds it to the list of managed listeners, and returns it.

        Args:
            status (StatusDocument): The status of documents to be fetched by the Listener.
            interval (int): The interval in seconds between each fetch operation.
            limit_documents (int): The maximum number of documents to fetch per request.

        Returns:
            Listener: The newly created and started Listener instance.
        """
        listener = Listener(
            self.api_client, status=status, interval=interval, limit_documents=limit_documents)
        listener.start()
        self.listeners.append(listener)
        return listener

    def stop_all_listeners(self):
        """
        Stop all active Listeners and clear the list.

        This method iterates through all managed Listeners, stops each one,
        and then clears the list of Listeners.
        """
        for listener in self.listeners:
            listener.stop()
        self.listeners.clear()