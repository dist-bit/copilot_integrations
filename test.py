from nebuia_copilot_python import integration
from loguru import logger

from nebuia_copilot_python.src.models import BatchType, EntityDocumentExtractor, EntityTextExtractor, File, Search, SearchParameters, StatusDocument

integrator = integration.Integrator(with_base='https://ia.nebuia.com/api/v1', key='2J7NFWQ-236PGAM-2S9RD3C-2DG54CY',
                                    secret='a47abf97-866b-4154-b29c-346c9b02919e')


# listener example


integrator.add_listener(
    status=StatusDocument.WAITING_QA, batchType=BatchType.EXECUTION, interval=4, limit_documents=20)



def on_document(status, doc):
    logger.info(f"getting document {status}: {doc}")
    
def on_listener_start(status):
    logger.debug(f"listener fro status {status} started")
    
integrator.listener.set_on_document_handler(on_document)
integrator.listener.set_on_listener_start_handler(on_listener_start)
    
integrator.listener.run()