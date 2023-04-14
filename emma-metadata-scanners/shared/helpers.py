import pytz
import iso639
import string
from datetime import datetime, timezone
from pprint import pprint

"""
Date/Time 
We'll work in PST since that's Bookshare's Point of View
"""
def get_now_iso8601_date_pst():
    utc_dt = datetime.now(timezone.utc)
    PST = pytz.timezone('US/Pacific')
    return utc_dt.astimezone(PST).date().isoformat()


def get_now_datetime_pst():
    utc_dt = datetime.now(timezone.utc)
    PST = pytz.timezone('US/Pacific')
    return utc_dt.astimezone(PST)


def get_today_iso8601_datetime_pst():
    return get_now_datetime_pst().isoformat()

def get_now_iso8601_datetime_utc():
    """
    UTC instead of PST for Internet Archive
    """
    utc_dt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc_dt

def get_languages(record):
    """
    I saw multiple language formats for language from different sources,
    so this attempts to translate all to the ISO 639-2 3-character code
    """
    if exists(record, 'language') and len(record['language']) > 0:
        incoming_language_list = listify(record['language'])
        language_list = []
        for incoming_language in incoming_language_list:
            language = get_language(incoming_language)
            if language is not None and len(language) > 0:
                language_list.append(language)
        return language_list


def get_language(incoming_language):
    """
    Translate the incoming language code into ISO 639-2 3-character code if possible
    The iso639 library is not great about handling keys that don't exist, hence
    all of the exception handling.
    """
    language = None
    try:
        language = iso639.languages.get(part1=incoming_language.lower())
    except KeyError:
        pass
    if language is None:
        try:
            language = iso639.languages.get(part3=incoming_language.lower())
        except KeyError:
            pass
    if language is None:
        try:
            language = iso639.languages.get(part2b=incoming_language.lower())
        except KeyError:
            pass
    if language is None:
        try:
            language = iso639.languages.get(part2t=incoming_language.lower())
        except KeyError:
            pass
    if language is None:
        try:
            language = iso639.languages.get(name=string.capwords(incoming_language))
        except KeyError:
            pass
    if language is not None:
        return language.part2b
    return None


def exists(record, field_name):
    """
    Our definition of whether a field exists in a Python dict 
    """
    return field_name in record and record[field_name] is not None

def listify(prop):
    """
    If a single property is not  a list but should be, convert to a single-element list
    """
    return prop if isinstance(prop, list) else [prop] 

def stringify(prop):
    """
    If a single property is not  a string but should be, convert to a string
    """
    return prop if not isinstance(prop, list) else " ".join(prop)

def batch(iterable, batch_size=1):
    """
    Batches iterables in even batches of n length, until the last batch, which runs until the end.
    Batch size defaults to 1.
    """
    if batch_size < 1:
        raise ValueError(f"Batch size can not be less than 1: {batch_size}")
    length = len(iterable)
    for ndx in range(0, length, batch_size):
        yield iterable[ndx:min(ndx + batch_size, length)]