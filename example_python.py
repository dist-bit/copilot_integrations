from nebuia_copilot_python import integration
from loguru import logger

from nebuia_copilot_python.src.models import BatchType, EntityDocumentExtractor, EntityTextExtractor, File, Search, SearchParameters, StatusDocument

integrator = integration.Integrator(with_base='http://nebuia.instance/api/v1', key='api_key',
                                    secret='api_secret')

files = [File(
    file="https://domain.com/file.pdf",  # "/path/to/file.pdf", bytes
    type_document="uuid_type_document"
)]

# perform search on custom brain
results = integrator.search_in_brain(search_params=SearchParameters(
    batch="brain_id", param="gripa", k=2, type_search="semantic"))
logger.info(results)

search_result = integrator.search_in_document(search=Search(matches="determinacion", uuid="uuid", max_results=1))
logger.info(search_result)

# get documents by status (supports pagination)
docs = integrator.get_documents_by_status(status=StatusDocument.ERROR_LINK)
logger.info(docs)

# clear document by uuid for reprocessing
status = integrator.clear_document_by_uuid("uuid_document")
logger.info(status)

# delete document by uuid
delete = integrator.delete_document("uuid_document")
logger.info(delete)

# delete batch id
delete = integrator.delete_batch("id_batch")
logger.info(delete)

# append documents to extractor inference
status = integrator.process_document_in_batch("batch_id")
logger.info(status)

# get document by uud
document = integrator.get_document_by_uuid("uuid_document")
logger.info(document)

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
integrator.add_listener(
    status=StatusDocument.QA_COMPLETE, batchType=BatchType.EXECUTION, interval=4, limit_documents=20)

integrator.add_listener(
    status=StatusDocument.WAITING_QA, batchType=BatchType.EXECUTION, interval=4, limit_documents=20)


def on_document(status, doc):
    logger.info(f"getting document {status}: {doc}")
    
def on_listener_start(status):
    logger.debug(f"listener fro status {status} started")
    
integrator.listener.set_on_document_handler(on_document)
integrator.listener.set_on_listener_start_handler(on_listener_start)
    
integrator.listener.run()


# extract entities from any text (in free version limit to 256 tokens)
entities = integrator.extract_entities_from_text(EntityTextExtractor(
    text="John Doe is 30 years old and lives in New York",
    schema={
        "name": "",
        "age": "",
        "location": ""
    }
))

logger.info(entities)

# extract entities from processed documents
entities = integrator.extract_entities_from_document_with_uuid("uuid_document", EntityDocumentExtractor(
    matches="protocolo web3",
    schema={
        "networks": []
    }
))

logger.info(entities)
