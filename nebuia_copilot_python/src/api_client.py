from datetime import datetime
import json
import time
from typing import ChainMap, Dict, List
import requests
from loguru import logger
from nebuia_copilot_python.src.models import BatchDocumentsResponse, BatchType, Document, DocumentType, Entity, File, Job, Response, Result, ResultsSearch, SearchParameters, StatusDocument, UploadResult
from requests_toolbelt import MultipartEncoder


class APIClient:
    def __init__(self, key: str, secret: str, base: str):
        self.key = key
        self.secret = secret
        self.base_url = base
        self.headers = {
            "key": self.key,
            "secret": self.secret
        }


    def set_document_status(self, uuid: str, status: StatusDocument) -> bool:
        """
        Set the status of a document identified by its UUID.

        This method updates the status of a document in the system by making a GET request
        to the specified URL with the document's UUID and the new status.

        Args:
            uuid (str): The UUID of the document whose status is to be updated.
            status (StatusDocument): The new status to be set for the document.

        Returns:
            bool: True if the status was successfully updated, False otherwise.

        Raises:
            requests.exceptions.RequestException: If there is an issue with the network request.
            ValueError: If the response JSON does not contain a 'status' key.

        Example:
            >>> set_document_status('uuid_document', StatusDocument.APPROVED)
            True
        """
        url = f"{self.base_url}/integrator/documents/set/status/{uuid}/{status.value}"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        return data['status']

    def get_documents_by_status(self, status: StatusDocument, page: int = 1, limit: int = 10) -> BatchDocumentsResponse:
        """
        Fetches a batch of documents based on their status from the API.

        This method constructs a URL using the provided status, page, and limit parameters,
        then makes an HTTP GET request to retrieve the documents. The response is parsed
        and converted into a list of Document objects, which are then returned along with
        the total count of documents.

        Args:
            status (StatusDocument): The status of the documents to fetch. This should be an
                enum value representing the document status.
            page (int, optional): The page number of the results to fetch. Defaults to 1.
            limit (int, optional): The number of documents to fetch per page. Defaults to 10.

        Returns:
            BatchDocumentsResponse: An object containing a list of Document objects and the
                total count of documents matching the query.

        Raises:
            requests.RequestException: If there is an error while making the HTTP request.
            KeyError: If there is an error parsing the response data due to missing keys.
            ValueError: If there is an error parsing the response data due to invalid values.
        """
        url = f"{self.base_url}/integrator/documents/by/status/{
            status.value}?page={page}&limit={limit}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            payload = data.get('payload', {})
            documents_data = payload.get('documents', [])

            documents = []
            if not documents_data:
                return BatchDocumentsResponse(
                    documents=documents,
                    total=payload['total']
                )

            for doc_data in documents_data:
                entities = None
                if 'entities' in doc_data:
                    entities = [
                        Entity(
                            id=entity['id'],
                            key=entity['key'],
                            value=entity['value'],
                            page=entity['page'],
                            id_core=entity['id_core'],
                            is_valid=entity['is_valid']
                        ) for entity in doc_data['entities']
                    ]

                document = Document(
                    id=doc_data['id'],
                    batch_id=doc_data['batch_id'],
                    user=doc_data['user'],
                    uuid=doc_data['uuid'],
                    url=doc_data['url'],
                    file_name=doc_data['file_name'],
                    type_document=doc_data['type_document'],
                    status_document=doc_data['status_document'],
                    uploaded=datetime.fromisoformat(
                        doc_data['uploaded'].rstrip('Z')),
                    reviewed_at=datetime.fromisoformat(
                        doc_data['reviewed_at'].rstrip('Z')),
                    source_type=doc_data['source_type'],
                    entities=entities
                )
                documents.append(document)

            return BatchDocumentsResponse(
                documents=documents,
                total=payload['total']
            )

        except requests.RequestException as e:
            logger.error(f"Error fetching documents: {e}")
            raise

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing response data: {e}")
            raise

    def get_documents_by_batch(self, id_batch: str, page: int = 1, limit: int = 10) -> BatchDocumentsResponse:
        """
        Retrieve documents associated with a specific batch ID.

        This method sends a GET request to the server to fetch all documents
        linked to the provided batch ID. It processes the response and returns
        a structured representation of the documents and their details.

        Args:
            id_batch (str): The ID of the batch for which to retrieve documents.

        Returns:
            BatchDocumentsResponse: An object containing a list of Document objects
            and the total count of documents.

        Raises:
            requests.RequestException: If there's an error in the HTTP request.
            ValueError: If the response from the server is not in the expected format.
            KeyError: If the response is missing expected fields.

        Example:
            >>> batch_response = integrator.get_documents_by_batch("66a5271a7a97c83cece5dd0d")
            >>> print(f"Total documents: {batch_response.total}")
            >>> for doc in batch_response.documents:
            ...     print(f"Document: {doc.file_name}, Status: {doc.status_document}")

        Note:
            The 'entities' field in each document is optional and will be included
            only if present in the API response.
        """
        url = f"{self.base_url}/integrator/documents/by/id/batch/{id_batch}?page={page}&limit={limit}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            payload = data.get('payload', {})
            documents_data = payload.get('documents', [])

            if not documents_data:
                return BatchDocumentsResponse(
                    documents=documents,
                    total=payload['total']
                )

            documents = []
            for doc_data in documents_data:
                entities = None
                if 'entities' in doc_data:
                    entities = [
                        Entity(
                            id=entity['id'],
                            key=entity['key'],
                            value=entity['value'],
                            page=entity['page'],
                            id_core=entity['id_core'],
                            is_valid=entity['is_valid']
                        ) for entity in doc_data['entities']
                    ]

                document = Document(
                    id=doc_data['id'],
                    batch_id=doc_data['batch_id'],
                    user=doc_data['user'],
                    uuid=doc_data['uuid'],
                    url=doc_data['url'],
                    file_name=doc_data['file_name'],
                    type_document=doc_data['type_document'],
                    status_document=doc_data['status_document'],
                    uploaded=datetime.fromisoformat(
                        doc_data['uploaded'].rstrip('Z')),
                    reviewed_at=datetime.fromisoformat(
                        doc_data['reviewed_at'].rstrip('Z')),
                    source_type=doc_data['source_type'],
                    entities=entities
                )
                documents.append(document)

            return BatchDocumentsResponse(
                documents=documents,
                total=payload['total']
            )

        except requests.RequestException as e:
            logger.error(f"Error fetching documents: {e}")
            raise

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing response data: {e}")
            raise

    def clear_document_by_uuid(self, uuid: str) -> bool:
        """
        Clears a document from the system using its unique identifier (UUID).

        This method constructs a URL based on the provided UUID and sends a GET request
        to clear the specified document from the system. The response from the server is
        then parsed as JSON, and the method returns the status of the operation.

        Args:
            uuid (str): The unique identifier of the document to be cleared.

        Returns:
            bool: True if the document was cleared successfully, False otherwise.

        Raises:
            requests.exceptions.RequestException: If there is an issue with the network
                                                or the server response.

        Example:
            >>> result = self.clear_document_by_uuid("some-unique-identifier")
            >>> print(result)
            True
        """
        url = f"{self.base_url}/integrator/clear/document/{uuid}"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        return data['status']

    def delete_batch(self, batch_id: str) -> bool:
        """
        Deletes a batch with the specified batch ID.

        This method sends a DELETE request to the integrator API to remove a batch
        identified by the given batch ID. It returns a boolean indicating whether
        the deletion was successful.

        Args:
            batch_id (str): The unique identifier of the batch to be deleted.

        Returns:
            bool: True if the batch was successfully deleted, False otherwise.

        Raises:
            HTTPError: If the DELETE request returns an unsuccessful status code.
            JSONDecodeError: If the response content cannot be decoded as JSON.
            KeyError: If the 'status' key is not found in the response JSON.
        """
        url = f"{self.base_url}/integrator/delete/batch/{batch_id}"
        response = requests.delete(url, headers=self.headers)
        data = response.json()
        return data['status']

    def delete_document_from_batch(self, uuid: str) -> bool:
        """
        Deletes a document from a batch using its unique identifier (UUID).

        This method constructs a URL based on the provided UUID and sends a DELETE request
        to remove the specified document from the batch. The response from the server is
        then parsed as JSON and returned.

        Args:
            uuid (str): The unique identifier of the document to be deleted.

        Returns:
            bool: bool containing information about the success or failure of the deletion operation.

        Raises:
            requests.exceptions.RequestException: If there is an issue with the network
                                                or the server response.

        Example:
            >>> result = self.delete_document_from_batch("some-unique-identifier")
            >>> print(result)
            True
        """
        url = f"{self.base_url}/integrator/delete/by/uuid/{uuid}"
        response = requests.delete(url, headers=self.headers)
        data = response.json()
        return data['status']

    def get_document_types(self) -> List[DocumentType]:
        """
        Retrieves all document types for the user.

        This method sends a GET request to the server to fetch all document types
        associated with the current user.

        Returns:
            List[DocumentType]: A list of DocumentType objects representing the 
            different document types available for the user.

        Raises:
            requests.RequestException: If there's an error in the HTTP request.
            ValueError: If the response from the server is not in the expected format.

        Example:
            >>> document_types = integrator.get_document_types()
            >>> for doc_type in document_types:
            ...     print(f"{doc_type.key}: {doc_type.id_type_document}")
        """
        url = f"{self.base_url}/integrator/documents/type/all/user"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            json_data = response.json()
            payload = json_data.get('payload', [])

            return [
                DocumentType(
                    id=item['id'],
                    user=item['user'],
                    key=item['key'],
                    id_type_document=item['id_type_document'],
                    created=datetime.fromisoformat(item['created'].rstrip('Z'))
                )
                for item in payload
            ]

        except requests.RequestException as e:
            logger.error(f"Error fetching document types: {e}")
            return []

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing response data: {e}")
            return []

    def create_batch(self, name: str, batch_type: BatchType):
        """
        Creates a new batch with the specified name and type.

        Args:
            name (str): The name of the batch to be created.
            batch_type (BatchType): The type of the batch, which can be 'execution' or 'testing'.

        Returns:
            Response: An object containing the response payload and status.

        Raises:
            ValueError: If the provided batch type is not 'execution' or 'testing'.
            requests.HTTPError: If the HTTP request returns a status code other than 200.
        """
        if batch_type not in BatchType.__members__.values():
            raise ValueError(
                "Invalid batch type. Must be 'execution' or 'testing'.")

        url = f"{self.base_url}/integrator/create/batch"

        data = {
            "batch_name": name,
            "batch_type": batch_type.value
        }

        response = requests.post(url, headers=self.headers, data=data)

        if response.status_code == 200:
            json_data = response.json()
            return Response(json_data['payload'], json_data['status'])
        else:
            response.raise_for_status()

    def _upload_file(self, file: File, batch_id: str, max_retries: int = 3, retry_delay: int = 5) -> UploadResult:
        """
        Uploads a file to a specified batch on a remote server.

        Args:
            file (File): The file object to be uploaded. This object should have methods `get_file_data()`, `get_mime_type()`, and `get_filename()`.
            batch_id (str): The identifier of the batch to which the file should be appended.
            max_retries (int, optional): The maximum number of times to retry the upload if it fails. Defaults to 3.
            retry_delay (int, optional): The delay in seconds between each retry attempt. Defaults to 5.

        Returns:
            UploadResult: An object containing the result of the upload operation. It includes whether the upload was successful, the filename, a message, and the response data from the server.

        Raises:
            Logs an error message if an exception occurs during the upload process.
        """
        url = f"{self.base_url}/integrator/append/to/batch/{batch_id}"

        for attempt in range(max_retries):
            try:
                file_data = file.get_file_data()
                file_name = file.get_filename()
                mime_type = file.get_mime_type()

                if not isinstance(file_data, str):
                    m = MultipartEncoder(
                        fields={
                            'file': (file_name, file_data, mime_type),
                            'type_document': file.type_document
                        }
                    )
                else:
                    m = MultipartEncoder(
                        fields={
                            'file_url': file_data,
                            'file_name': file_name,
                            'mime_type': mime_type,
                            'type_document': file.type_document
                        }
                    )

                headers = {"Content-Type": m.content_type}
                headers_with_keys = dict(ChainMap(headers, self.headers))

                response = requests.post(
                    url, data=m, headers=headers_with_keys)
                response_data = response.json()

                if response_data['status']:
                    return UploadResult(True, file_name, uuid=response_data.get('payload', 'successful')[0])
                else:
                    if attempt == max_retries - 1:
                        return UploadResult(False, file_name, error_message=response_data.get('payload', 'unknown error'))
                    time.sleep(retry_delay)

            except Exception as e:
                if attempt == max_retries - 1:
                    return UploadResult(False, file_name, error_message=str(e))
                time.sleep(retry_delay)

        return UploadResult(False, file_name, error_message="max retries reached")

    def append_job(self, job: Job, batch_id: str, max_retries: int = 1, retry_delay: int = 5) -> Dict[str, List[UploadResult]]:
        """
        Processes a job by uploading all files associated with it to a specified batch.

        Args:
            job (Job): The job object containing a list of files to be uploaded.
            batch_id (str): The identifier of the batch to which the files should be appended.
            max_retries (int, optional): The maximum number of times to retry each file upload if it fails. Defaults to 1.
            retry_delay (int, optional): The delay in seconds between each retry attempt for each file upload. Defaults to 5.

        Returns:
            Dict[str, List[UploadResult]]: A dictionary containing two lists:
                - "successful": A list of UploadResult objects for successful uploads.
                - "failed": A list of UploadResult objects for failed uploads.
        """
        results = {
            "successful": [],
            "failed": []
        }

        for file in job.files:
            result = self._upload_file(
                file, batch_id, max_retries=max_retries, retry_delay=retry_delay)
            if result.success:
                results["successful"].append(result)
            else:
                results["failed"].append(result)

        return results

    def search_in_brain(self, search_params: SearchParameters) -> ResultsSearch:
        """
        Sends a search request to the API with the given search parameters and returns the results.

        Args:
            search_params (SearchParameters): The parameters for the search operation.

        Returns:
            ResultsResponse: The response containing the search results.

        Raises:
            requests.exceptions.RequestException: If the request to the API fails.
        """
        url = f"{self.base_url}/integrator/search/brain"

        payload = json.dumps(search_params.__dict__)
        response = requests.post(url, headers=self.headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_data = response.json()

        if not response_data['status']:
            return ResultsSearch(results=[])

        if not 'results' in response_data['payload']:
            return ResultsSearch(results=[])

        results = response_data["payload"]["results"]
        results = [Result(**result_data) for result_data in results]
        return results

    def process_item(self, batch_id: str) -> bool:
        """
        Processes an item within a specified batch.

        This method sends a POST request to the integrator API to run quality
        assurance (QA) on all items within a given batch. It logs the response if
        the request is successful, or logs an error message if the request fails.

        Args:
            batch_id (str): The identifier of the batch to process.

        Returns:
            None

        Raises:
            HTTPError: If the POST request returns an unsuccessful status code.
            JSONDecodeError: If the response content cannot be decoded as JSON.
        """
        url = f"{self.base}/integrator/run/qa/batch/all/{batch_id}"
        headers = {
            "key": self.key,
            "secret": self.secret,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data={})
        response_data = response.json()

        if response.status_code == 200:
            return response_data['status']
        else:
            logger.error(
                f"Error processing batch: {response_data.get('error', 'Unknown error')}")
            return False
