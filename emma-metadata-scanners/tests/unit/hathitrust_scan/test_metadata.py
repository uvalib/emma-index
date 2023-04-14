"""

"""
import logging
import csv
import io

from hathitrust_shared import metadata, metadata_constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_transform_lines():
    with open('tests/unit/examples/hathi_upd_20190927.txt', newline = '') as data_file:
        record_reader = csv.DictReader(data_file, delimiter='\t', fieldnames=metadata_constants.FIELD_NAMES)
        count = 0
        max_title_len = 0
        for line in record_reader:

            if metadata.ingestible_record(line) :
                result = metadata.transform_record(line)
                # logger.info(json.dumps(result, sort_keys=True, indent=4))

                assert len(result['emma_repositoryRecordId']) > 0
                assert result['emma_repository'] == 'hathiTrust'
                assert result['dc_format'] == 'pdf'
                assert len(result['dc_title']) <= metadata_constants.MAX_STRING_LENGTH
                if len(result['dc_title']) >= max_title_len:
                    max_title_len = len(result['dc_title'])
                count = count + 1
            else:
                pass

    assert count == 59
    logger.info("Processed " + str(count) + " lines")
    logger.info("Maximum title length: " + str(max_title_len))


def test_transform_complete_line():
    complete_line = 'mdp.39015084530909	allow	pd	002137795	no.1417	MIU	002137795	2127036		0093-1322	sf 89010707	Public Health Service publication.	U.S. Dept. of Health, Education, and Welfare, Public Health Service, Environmental Health Service, National Air Pollution Control Administration; For sale by the Supt. of Docs., U.S. G.P.O..	bib	2012-11-01 04:33:07	1	9999	dcu	eng	SE	MIU	umich	umich	google	google'
    record_reader = csv.DictReader(io.StringIO(complete_line), delimiter='\t', fieldnames=metadata_constants.FIELD_NAMES)
    for line in record_reader:
            result = metadata.transform_record(line)

    assert result['dc_description'] == 'no.1417'
    assert result['dc_format'] == 'pdf'
    assert set(result['dc_identifier']) == set(['issn:00931322', 'oclc:2127036', 'lccn:sf89010707'])
    assert result['dc_language'] == ['eng']
    assert result['dc_rights'] == 'publicDomain'
    assert result['dc_title'] == 'Public Health Service publication.'
    assert result['dcterms_dateAccepted'] == '2012-11-01T04:33:07'
    assert result['dcterms_dateCopyright'] == '9999'
    assert result['emma_collection'] == ['University of Michigan']
    assert result['emma_repository'] == 'hathiTrust'
    assert result['emma_repositoryRecordId'] == 'mdp.39015084530909'
    assert result['emma_retrievalLink'] == 'https://hdl.handle.net/2027/mdp.39015084530909'
    assert result['emma_webPageLink'] == 'https://hdl.handle.net/2027/mdp.39015084530909'
    assert result['s_accessMode'] == ['visual', 'textual']
    assert result['s_accessModeSufficient'] == ['visual', 'textual']
