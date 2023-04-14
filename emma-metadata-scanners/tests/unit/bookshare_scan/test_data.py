
FIRST_RECORD_ID = 11
PAGE_1_RECORD_2_ID = 12
PAGE_1_RECORD_3_ID = 13
PAGE_2_RECORD_1_ID = 21
PAGE_2_RECORD_2_ID = 22
PAGE_2_RECORD_3_ID = 23
PAGE_3_RECORD_1_ID = 31
LAST_RECORD_ID = 32


def get_page_1():
    with open('tests/unit/examples/full_page_1.json') as data_file:
        data = data_file.read()
        return data


def get_page_2():
    with open('tests/unit/examples/full_page_2.json') as data_file:
        data = data_file.read()
        return data


def get_partial_page_2():
    with open('tests/unit/examples/partial_page_2.json') as data_file:
        data = data_file.read()
        return data


def get_page_3():
    with open('tests/unit/examples/full_page_3_last.json') as data_file:
        data = data_file.read()
        return data


def get_bks_record_list():
    with open('tests/unit/examples/bks_record_list_only.json') as data_file:
        data = data_file.read()
        return data


def get_bks_bad_param_response():
    with open('tests/unit/examples/bks_bad_param_response.json') as data_file:
        data = data_file.read()
        return data


def get_bks_bad_start_param_response():
    with open('tests/unit/examples/bks_bad_start_param_500_err.json') as data_file:
        data = data_file.read()
        return data


def get_bks_unauthorized_response():
    with open('tests/unit/examples/bks_unauthorized_response.json') as data_file:
        data = data_file.read()
        return data

