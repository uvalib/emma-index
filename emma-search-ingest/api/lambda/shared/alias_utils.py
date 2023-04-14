
from shared.helpers import exists

'''
These fields have ElasticSearch aliases which we'll use until we can reindex
the ElasticSearch index into a new copy with the final field names.
'''
RENAMED_TO_DEPRECATED_FIELDS = {
    'rem_comments': 'emma_lastRemediationNote',
    'rem_remediationDate': 'emma_lastRemediationDate',
    'emma_repositoryUpdateDate': 'emma_repositoryMetadataUpdateDate'
}


def rename_to_backwards_compatible_deprecated_fields(document):
    """
    This is for schema versions where we must support a new and an old name for
    an ElasticSearch field.  The old field name will be given an alias of the new name.
    However, when inserting data, it must be inserted using the old name.
    Eventually, we will reindex the repository into a new copy with the updated field names
    and this will no longer be possible.
    """
    for new_field_name in RENAMED_TO_DEPRECATED_FIELDS:
        deprecated_field = RENAMED_TO_DEPRECATED_FIELDS[new_field_name]
        if exists(document, new_field_name):
            document[deprecated_field] = document[new_field_name]
            del document[new_field_name]


def copy_to_new_field_names(document):
    """
    This is for schema versions where we must support a new and an old name for
    an ElasticSearch field.
    The old name will be copied to the alias.
    See ElasticSearch documentation for aliases:
    'It’s important to note that field aliases cannot be used when indexing documents:
     a document’s source can only contain concrete fields. For this reason,
     field aliases don’t appear in the result of APIs like GET, which return the document source untouched.`
     https://www.elastic.co/blog/introducing-field-aliases-in-elasticsearch
     But we want result documents to include both the new and the old fields until the old fields are gone.
    """
    for new_field_name in RENAMED_TO_DEPRECATED_FIELDS:
        deprecated_field = RENAMED_TO_DEPRECATED_FIELDS[new_field_name]
        if exists(document, deprecated_field):
            document[new_field_name] = document[deprecated_field]
