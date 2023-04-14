Feature: SQS enable/disable tests


  Scenario: Disable SQS rules on Lambda functions
    Given we have scanner AWS Lambda functions
    When we disable the SQS triggers
    Then the SQS triggers are disabled


  Scenario: Enable SQS rules on Lambda functions
    Given we have scanner AWS Lambda functions
    When we enable the SQS triggers
    Then the SQS triggers are enabled
