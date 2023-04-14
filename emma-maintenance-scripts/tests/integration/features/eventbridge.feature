Feature: Eventbridge enable/disable tests

  Scenario: Disable event rules on Lambda functions
    Given we have scanner AWS Lambda functions
    And they are running on a timed schedule
    When we disable the timed triggers
    Then the timed triggers are disabled


  Scenario: Enable event rules on Lambda functions
    Given we have scanner AWS Lambda functions
    And they are running on a timed schedule
    When we enable the timed triggers
    Then the timed triggers are enabled

