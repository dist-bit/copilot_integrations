from nebuia_copilot_python.src.api_client import APIClient
from nebuia_copilot_python.src.models import EntityDocumentExtractor, EntityTextExtractor
from nebuia_copilot_python.src.utils import dict_to_indented_string, parse_json_or_return_string


class Extractor:
    """
    A class for handling text extraction operations using an API client.

    This class provides methods to extract information from text using
    a specified API client. It includes functionality to process and
    format extraction requests before sending them to the API.

    Attributes:
        api_client (APIClient): An instance of APIClient used to make API calls.

    Methods:
        extract_from_text(extractor: EntityTextExtractor) -> dict:
            Extracts information from text using the provided extractor configuration.
    """

    def __init__(self, api_client: APIClient):
        """
        Initializes the Extractor with an API client.

        Args:
            api_client (APIClient): An instance of APIClient to be used for API calls.
        """
        self.api_client = api_client

    def extract_from_text(self, extractor: EntityTextExtractor):
        """
        Extracts information from text using the provided extractor configuration.

        This method prepares the extractor configuration by converting its schema
        to an indented string format, then sends the extraction request to the API
        using the configured API client.

        Args:
            extractor (EntityTextExtractor): An object containing the text to be
                                             processed and the extraction schema.

        Returns:
            dict: The extracted information as returned by the API.

        Note:
            The 'schema' attribute of the extractor is modified in place,
            converting it to an indented string format before making the API call.
        """
        extractor.schema = dict_to_indented_string(extractor.schema)
        return parse_json_or_return_string(self.api_client.extractor_from_text(extractor))
    

    def extract_from_document_with_uuid(self, uuid: str, extractor: EntityDocumentExtractor):
        """
        Extracts information from a document identified by UUID using the provided extractor configuration.

        This method prepares the extractor configuration and sends it to the API client for processing.
        It then attempts to parse the API response as JSON, falling back to returning the raw response
        if parsing fails.

        Args:
            uuid (str): The unique identifier of the document to be processed.
            extractor (EntityDocumentExtractor): A dataclass object containing:
                - matches (str): Specifies the matching criteria for the extraction process.
                - schema (Union[str, dict]): The schema defining the entities to extract.
                If provided as a dict, it will be converted to an indented string.

        Returns:
            Union[dict, list, str]: The extracted information as a Python object (dict or list) 
                                    if the API response is valid JSON, or the raw response string 
                                    if JSON parsing fails.

        Raises:
            TypeError: If the schema is not a string or dict.
            Any exceptions that might be raised by the API client's extractor_from_document_uuid method.

        Note:
            - The schema in the EntityDocumentExtractor is converted to an indented string format
            if it's provided as a dict. This modification is done in-place on the extractor object.
            - The method uses a utility function (parse_json_or_return_string) to handle the API response,
            ensuring that even if the response is not valid JSON, the method will not raise an exception.
            - The 'matches' field in EntityDocumentExtractor is sent to the API as is, without modification.

        Example:
            uuid = "uuid_document"
            extractor = EntityDocumentExtractor(
                matches="keyword1 keyword2",
                schema={"name": "", "date": ""}
            )
            result = obj.extract_from_document_with_uuid(uuid, extractor)
        """
        extractor.schema = dict_to_indented_string(extractor.schema)
        return parse_json_or_return_string(self.api_client.extractor_from_document_uuid(uuid=uuid, data=extractor))
