from dataclasses import dataclass
from datetime import datetime
import enum
import os
from typing import Any, List, Literal, Optional, Union
from urllib.parse import urlparse
import magic

from nebuia_copilot_python.src.utils import check_downloadable_file


class BatchType(enum.Enum):
    EXECUTION = "execution"
    TESTING = "testing"


class StatusDocument(enum.Enum):
    WAITING_PROCESS = "waiting_process"
    WORKING_OCR = "working_extractor"
    
    PROCESSED = "processed"
    COMPLETE = "complete"

    ERROR_LINK = "error_download_link"
    ERROR_OCR = "error_on_extraction"

    ASSIGNED = "assigned"
    WAITING_QA = "waiting_qa"
    WORKING_QA = "working_qa"
    QA_COMPLETE = "complete_qa"
    NO_PIPELINE_DEFINED = "no_pipeline_defined"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"
    REVIEWED = "reviewed"

    WITH_ERROR_ON_ASSIGN = "with_error_on_assign"


@dataclass
class Response:
    payload: Any
    status: bool


class File:
    """
    Represents a file that can be either a local file path, a URL, or binary data.

    This class provides methods to handle different types of file inputs,
    retrieve file data, determine MIME type, and manage filenames.

    Attributes:
        file (Union[str, bytes]): The file data, which can be a string (path or URL) or bytes.
        type_document (str): The id of type document.
        filename (Optional[str]): The filename, if provided. If not, it is inferred from the file data.
    """

    def __init__(self, file: Union[str, bytes], type_document: str, filename: Optional[str] = None):
        """
        Initializes a new instance of the File class.

        Args:
            file (Union[str, bytes]): The file data, which can be a string (path or URL) or bytes.
            type_document (str): The type of document, such as 'image', 'pdf', etc.
            filename (Optional[str]): The filename, if provided. If not, it is inferred from the file data.
        """
        self.file = file
        self.type_document = type_document
        self.filename = filename if filename else self._get_filename()

    def _get_filename(self):
        """
        Infers the filename from the file data.

        Returns:
            str: The inferred filename.

        Raises:
            ValueError: If the file type is unsupported.
        """
        if isinstance(self.file, str):
            if self.file.startswith('http'):
                parsed_url = urlparse(self.file)
                return os.path.basename(parsed_url.path) or 'downloaded_file'
            else:
                return os.path.basename(self.file)
        elif isinstance(self.file, bytes):
            return 'binary_data'
        else:
            raise ValueError("Unsupported file type")

    def get_file_data(self):
        """
        Retrieves the file data, handling different types of file inputs.

        Returns:
            bytes: The file data.

        Raises:
            ValueError: If the file type is unsupported.
            HTTPError: If the URL request returns an unsuccessful status code.
        """
        if isinstance(self.file, str):
            if self.file.startswith('http'):
                url, mime_type = check_downloadable_file(self.file)
                if url != None:
                    self.mime_type = mime_type
                    return url
            else:
                with open(self.file, 'rb') as f:
                    file_data = f.read()
                self.mime_type = magic.from_buffer(file_data[:8], mime=True)
                return file_data
        elif isinstance(self.file, bytes):
            self.mime_type = magic.from_buffer(self.file[:8], mime=True)
            return self.file
        else:
            raise ValueError("Unsupported file type")

    def get_mime_type(self):
        """
        Retrieves the MIME type of the file.

        Returns:
            str: The MIME type of the file.
        """
        if not hasattr(self, 'mime_type'):
            self.get_file_data()
        return self.mime_type

    def get_filename(self):
        """
        Retrieves the filename.

        Returns:
            str: The filename.
        """
        return self.filename


@dataclass
class Job:
    files: List[File]


@dataclass
class UploadResult:
    success: bool
    file_name: str
    uuid: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class DocumentType:
    id: str
    user: str
    key: str
    id_type_document: str
    created: datetime


@dataclass
class Entity:
    """
    Represents an entity identified within a document.

    Attributes:
        id (str): The unique identifier for the entity.
        key (str): The key or type of the entity (e.g., 'name', 'date').
        value (str): The value or content of the entity.
        page (int): The page number where the entity was found in the document.
        id_core (str): The identifier of the core where the entity was extracted.
        is_valid (bool): Indicates whether the entity is valid or not.
    """
    id: str
    key: str
    value: str
    page: int
    id_core: str
    is_valid: bool


@dataclass
class Document:
    """
    Represents a document with its associated metadata and entities.

    Attributes:
        id (str): The unique identifier for the document.
        batch_id (str): The identifier of the batch to which the document belongs.
        user (str): The user who uploaded the document.
        uuid (str): The universally unique identifier for the document.
        url (str): The URL where the document is stored.
        file_name (str): The name of the file.
        type_document (str): id for type document.
        status_document (str): The processing status of the document.
        uploaded (datetime): The date and time when the document was uploaded.
        reviewed_at (datetime): The date and time when the document was last reviewed.
        source_type (str): The source type of the document.
        entities (Optional[List[Entity]]): A list of entities identified within the document.
    """
    id: str
    batch_id: str
    user: str
    uuid: str
    url: str
    file_name: str
    type_document: str
    status_document: str
    uploaded: datetime
    reviewed_at: datetime
    source_type: str
    entities: Optional[List[Entity]] = None


@dataclass
class BatchDocumentsResponse:
    """
    Represents a response containing a list of documents and their total count.

    Attributes:
        documents (List[Document]): A list of documents included in the response.
        total (int): The total number of documents in the response.
    """
    documents: List[Document]
    total: int


@dataclass
class SearchParameters:
    """
    Represents the parameters for a search operation.

    Attributes:
        batch (str): The identifier of the batch.
        param (str): The parameter to search for.
        k (int): The number of results to return.
        type_search (Literal['semantic', 'literal']): The type of search to perform, either 'semantic' or 'literal'.
    """
    batch: str
    param: str
    k: int
    type_search: Literal['semantic', 'literal']


@dataclass
class Result:
    """
    Represents a result item from a search or query.

    Attributes:
        uuid (str): The unique identifier for the result.
        content (str): The content or text associated with the result.
        source (Union[int, str]): The source identifier from which the result was obtained, which can be an integer or a string.
        coincidences (int): The number of coincidences or matches found in the content.
        score (float): The score or relevance of the result.
    """
    uuid: str
    content: str
    name: Optional[str]
    source: Union[int, str]
    coincidences: int
    score: float


@dataclass
class ResultsSearch:
    """
    Represents a response containing a list of results.

    Attributes:
        results (List[Result]): A list of result items.
    """
    results: List[Result]
