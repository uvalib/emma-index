"""
Handler for bulk metadata record delete requests.
"""

from elasticsearch import helpers
from shared.helpers import get_doc_id

class DeleteHandler:
    def __init__(self, index, validator):
        self.validator = validator
        self.index = index

    def submit(self, es, document_list, errors):
        bulk_delete = []
        doc_count = 1

        '''
        We want the call to be idempotent, so 'Not Found' documents will be recorded as non-error messages
        If you rerun the bulk delete submission, and the deletions succeeded the first time, 
        you will continue to get a successful HTTP Status code, but a list of not found documents will be returned as well
        '''
        not_found_results = {}

        for document in document_list:
            if self.validator.validate(document, doc_count, errors):
                upsert_doc = self.create_delete_doc(es, document)
                bulk_delete.append(upsert_doc)
            doc_count = doc_count + 1
        try:
            helpers.bulk(es, bulk_delete)
        except helpers.BulkIndexError as e:
            for index_error in e.errors:
                if 'delete' in index_error:
                    delete_error = index_error['delete']
                    if '_id' in delete_error :
                        if 'status' in delete_error \
                            and str(delete_error['status']) == '404' :
                            not_found_results[delete_error['_id']] = ['Document not found']
                            # Not found should be idempotent, but not errors
                        elif 'result' in delete_error:
                            errors[delete_error['_id']] = [delete_error['status']]
                    else:
                        errors['indexing_result'] = ['Error from index', str(delete_error)]
                else:
                    errors['indexing_result'] = ['Error from index', str(index_error)]
        return not_found_results


    def create_delete_doc(self, es, document):
        """
        Wrap the request body for ElasticSearch
        """
        doc_id = get_doc_id(document)
        document['emma_recordId'] = doc_id
        delete_doc = {
            '_op_type': 'delete',
            '_index': self.index,
            '_id': doc_id,
        }
        return delete_doc

