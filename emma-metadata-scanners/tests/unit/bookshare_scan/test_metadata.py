import json

from bookshare_shared import metadata
from tests.unit.bookshare_scan import test_data


def test_transform():
    """
    Test that metadata records are appropriately transformed from
    Bookshare API results format to EMMA Ingestion format
    """
    # Set up the data
    json_object = json.loads(test_data.get_bks_record_list())

    # Run the test
    transformed_records = metadata.transform_records(json_object)

    # Check the results

    assert len(json_object) == 8
    assert len(transformed_records) > 8
    for sample_record in transformed_records:
        assert len(sample_record['dc_identifier']) > 0
        assert len(sample_record['dc_title']) > 0
        assert len(sample_record['dc_creator']) > 0
        assert len(sample_record['dc_format']) > 0
        assert len(sample_record['dc_subject']) > 0
        assert len(sample_record['dc_language']) > 0
        assert len(sample_record['emma_repository']) > 0
        assert len(sample_record['emma_repositoryRecordId']) > 0
        assert len(sample_record['emma_retrievalLink']) > 0

