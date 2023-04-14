Feature: Simple Ingestion Test

  Scenario: Ingest good record
     Given we create a metadata record
      When we submit the record
      Then we get a successful ingestion code

  Scenario: Get record
     Given we specify a metadata record
      When we request the record
      Then we get the record metadata

  Scenario: Delete record
     Given we specify a metadata record
      When we delete the record
      Then we get a successful deletion code