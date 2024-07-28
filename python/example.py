from integration import BatchType, File, Integrator, StatusDocument, SearchParameters
from loguru import logger

integrator = Integrator(with_base='http://nebuia.instance/api/v1', key='api_key',
                        secret='api_secret')

files = [File(
    file="https://domain.com/file.pdf",
    type_document="7d6528a4-2ad9-437c-9a32-bd1b869c0388"
)]

# perform search on custom brain
results = integrator.search_in_brain(search_params=SearchParameters(batch="brain_id", param="gripa", k=2, type_search="semantic"))
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
results = integrator.append_to_batch(batch_id="66a5271a7a97c83cece5dd0d", files=files)
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
status, batch_id = integrator.create_batch("name_batch", batch_type=BatchType.TESTING)
logger.info(status, batch_id)