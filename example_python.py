from nebuia_copilot_python import integration
from loguru import logger

from nebuia_copilot_python.src.models import BatchType, File, SearchParameters, StatusDocument

integrator = integration.Integrator(with_base='http://nebuia.instance/api/v1', key='api_key',
                                    secret='api_secret')

files = [File(
    file="https://domain.com/file.pdf", # "/path/to/file.pdf", bytes
    type_document="uuid_type_document"
)]

# perform search on custom brain
results = integrator.search_in_brain(search_params=SearchParameters(
    batch="brain_id", param="gripa", k=2, type_search="semantic"))
logger.info(results)

# get documents by status (supports pagination)
docs = integrator.get_documents_by_status(status=StatusDocument.ERROR_LINK)
logger.info(docs)

# clear document by uuid for reprocessing
status = integrator.clear_document_by_uuid("uuid_document")
logger.info(status)

# delete document by uuid
delete = integrator.delete_document("uuid_document")
logger.info(delete)

# get all documents from batch id
documents = integrator.get_documents_by_batch_id("batch_id")
for doc in documents.documents:
    print(f"Document: {doc.file_name}, Status: {doc.status_document}")

# add files to batch id
results = integrator.append_to_batch(batch_id="batch_id", files=files)
if len(results['failed']) > 0:
    for result in results['failed']:
        logger.info(result.file_name)
        logger.info(result.error_message)
else:
    for result in results['successful']:
        logger.info(result.file_name)
        logger.info(result.uuid)

# get documents types
document_types = integrator.get_document_types()
for doc_type in document_types:
    logger.info(f"{doc_type.key}: {doc_type.id_type_document}")

# create new batch
status, batch_id = integrator.create_batch(
    "name_batch", batch_type=BatchType.TESTING)
logger.info(status, batch_id)

# listener example
listener = integrator.add_listener(
    status=StatusDocument.WAITING_QA, interval=4, limit_documents=20)
try:
    for documents in listener.results():
        data = documents.documents
        for document in data:
            logger.info(f"Received documents: {document.uuid}")
            # set to complete
            # integrator.set_document_status(document.uuid, StatusDocument.COMPLETE)
            break
except KeyboardInterrupt:
    listener.stop()
    logger.warning("Stopped listener.")
