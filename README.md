# Nebuia Integration Library

This library provides an interface to interact with the Nebuia API, allowing operations for document processing, custom brain searching, and batch management.

## Key Features

- Integrator initialization with API credentials
- Custom brain searching
- Document management (retrieve, clear, delete)
- Batch handling (create, get documents, add files)
- Document type retrieval

## Installation

[Specific installation instructions for each language]

## Basic Usage

```[language]
# Integrator initialization
integrator = Integrator(with_base='http://nebuia.instance/api/v1', key='api_key', secret='api_secret')

# Usage example: Custom brain search
results = integrator.search_in_brain(search_params=SearchParameters(batch="brain_id", param="flu", k=2, type_search="literal"))

# Usage example: Get documents by status
docs = integrator.get_documents_by_status(status=StatusDocument.ERROR_LINK)

# Usage example: Create a new batch
status, batch_id = integrator.create_batch("name_batch", batch_type=BatchType.TESTING)
```

## API Reference

### Integrator Class

#### Main Methods:

- `search_in_brain(search_params: SearchParameters) -> dict`
- `get_documents_by_status(status: StatusDocument) -> list`
- `clear_document_by_uuid(uuid: str) -> dict`
- `delete_document(uuid: str) -> dict`
- `get_documents_by_batch_id(batch_id: str) -> BatchDocuments`
- `append_to_batch(batch_id: str, files: list[File]) -> dict`
- `get_document_types() -> list[DocumentType]`
- `create_batch(name: str, batch_type: BatchType) -> tuple[bool, str]`

### Data Structures

- `File`: Represents a file to process
- `SearchParameters`: Parameters for brain searching
- `StatusDocument`: Enumeration of document statuses
- `BatchType`: Enumeration of batch types

## Error Handling

The library uses the Loguru logger to log information and errors. Make sure to configure Loguru appropriately in your application.

## Implementation Notes

- The library should handle API responses and convert them into appropriate data structures for each language.
- Input validations should be implemented for method parameters.
- Error handling should be consistent across all methods, using specific exceptions when appropriate.

## Contributions

[Instructions for contributing to the project]

## License

[License information]
