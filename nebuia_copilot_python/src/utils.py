import json
import requests
import magic


def parse_json_or_return_string(input_string):
    """
    Try to parse the input string as JSON. If successful, returns the corresponding Python object.
    If it fails, returns the original unmodified string.

    Args:
    input_string (str): original string response.

    Returns:
    Union[dict, list, str]: json object.
    """
    try:
        return json.loads(input_string)
    except json.JSONDecodeError:
        return input_string


def dict_to_indented_string(dictionary, indent=4):
    """
    Convert dict to json.

    Args:
    dictionary (dict): dict to convert.
    indent (int): ident space 4.

    Returns:
    str: dict in string format.
    """
    return json.dumps(dictionary, indent=indent, ensure_ascii=False)


def check_downloadable_file(url: str) -> tuple:
    """
    Check if the file at the given URL is downloadable and determine its MIME type.

    This function attempts to retrieve the file's MIME type by performing a HEAD request followed by a GET request.
    It specifically checks if the MIME type is either "application/pdf" or an audio type.

    Args:
        url (str): The URL of the file to check.

    Returns:
        tuple: A tuple containing the URL and the MIME type if the file is downloadable and matches the criteria,
               otherwise returns (None, None).

    Raises:
        requests.RequestException: If there is an issue with the HTTP request (handled internally).
    """
    try:
        response = requests.head(url, allow_redirects=False)
        response.raise_for_status()

        response = requests.get(url)
        response.raise_for_status()

        mime_type = magic.from_buffer(response.content[:8], mime=True)

        if mime_type == "application/pdf" or "audio/" in mime_type:
            return url, mime_type

        return None, None
    except requests.RequestException:
        return None, None
