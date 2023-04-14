import json
from jsonschema import Draft7Validator, ValidationError

class EmmaValidator:

    def __init__(self, schema_file_name):
        self.schema_file_name = schema_file_name
        self.validator = Draft7Validator(self.load_validation_file(schema_file_name))


    def load_validation_file(self, schema_file_name) -> str:
        """
        Load the jsonSchema for an ingestion record into a data structure
        """
        with open(schema_file_name, 'r') as schema_file:
            data = schema_file.read()
            return json.loads(data)

    def validate(self, doc, doc_count, errors) -> bool:
        """
        Validate the current document against the jsonSchema corresponding to our OpenAPI definition
        If the document fails, return false and save validator error messages to the error list
        """    
        try:
            self.validator.validate(doc)
            return True
        except ValidationError:
            error_set = []
            for error in self.validator.iter_errors(doc):
                err_path = map(lambda x: str(x), error.path)
                error_set.append(','.join(err_path) + " : " + error.message)
            errors['document-' + str(doc_count)] = error_set
        return False