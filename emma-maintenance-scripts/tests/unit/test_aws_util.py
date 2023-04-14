import pytest
import shared.aws_util
import json
from datetime import datetime

from shared import aws_util


def test_q_query_numeric_creation():
    # Set up the data
    test_json = {
        "Name": "Bella",
        "Description": "Dog",
        "Properties": {
            "DateCreated": datetime.now(),
            "License": True,
            "Vaccinated": True,
            "Colors": ["Black", "White", "Brown", datetime.now()]
        },
        "Vaccinations": ["Rabies", "COVID-19", "Canine Flu", {"Name": "Distemper", "Expires": datetime.now()}],
        "DateUpdated": datetime.now()
    }

    fixed = aws_util.fix_dates_aws_for_json(test_json)
    print(json.dumps(fixed, indent=4))
