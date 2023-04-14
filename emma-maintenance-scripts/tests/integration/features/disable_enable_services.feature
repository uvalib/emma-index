Feature: All services enable/disable tests


  Scenario: Disable all services
    Given we have an ingestion API gateway, and scanners feeding into that gateway
    When we disable the ingestion services
    Then the services are disabled

  Scenario: Enable all services
    Given we have an ingestion API gateway, and scanners feeding into that gateway
    When we enable the ingestion services
    Then the services are enabled

  Scenario: Verify all services
    Given we have an ingestion API gateway, and scanners feeding into that gateway
    Then the services are enabled