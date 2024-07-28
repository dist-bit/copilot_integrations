import requests
import magic


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