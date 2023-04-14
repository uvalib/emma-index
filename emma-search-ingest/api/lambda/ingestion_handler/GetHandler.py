"""
Handler for requests to get multiple records from the federated index.
"""

from elasticsearch_dsl import Document

from shared.alias_utils import copy_to_new_field_names
from shared.helpers import get_doc_id, listify_record

class GetHandler:
    def __init__(self, index, validator):
        self.validator = validator
        self.index = index

    def submit(self, es, document_list, errors) -> list:
        multi_get = []
        doc_count = 1
        for document in document_list:
            if self.validator.validate(document, doc_count, errors):
                doc_id = get_doc_id(document)
                multi_get.append(doc_id) 
            doc_count = doc_count + 1
        es_response = Document.mget(using=es, docs=multi_get, index=self.index, raise_on_error=True, missing='none')
        transformed_results = []

        for doc in es_response:
            if doc is not None:
                record = listify_record(doc.to_dict())
                copy_to_new_field_names(record)
                transformed_results.append(record)
        return transformed_results
