Feature: API Gateway enable/disable tests


  Scenario: Disable Ingestion API Gateway
    Given we have an ingestion API gateway
    When we disable the API gateway
    Then the API gateway is disabled


  Scenario: Enable Ingestion API Gateway
    Given we have an ingestion API gateway
    When we enable the API gateway
    Then the API gateway is enabled


