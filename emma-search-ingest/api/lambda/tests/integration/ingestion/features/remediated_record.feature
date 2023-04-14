Feature: Remediated Record Ingestion Test

  Scenario: Ingest remediated good record
     Given we create a remediated metadata record
      When we submit the record
      Then we get a successful ingestion code

  Scenario: Get remediated record
     Given we specify a remediated metadata record
      When we request the record
      Then we get the record metadata

  Scenario: Delete remediated record
     Given we specify a remediated metadata record
      When we delete the record
      Then we get a successful deletion code