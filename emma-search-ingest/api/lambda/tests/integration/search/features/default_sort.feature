Feature: Default/relevance sort tests


  Scenario: Quick search with default sort
    Given We quick search for "the wind in the willows"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title


  Scenario: Individual field search with default sort
    Given We search on individual parameters
    And title as "the wind in the willows"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title


  Scenario: Quick search with default sort and format filter
    Given We quick search for "the wind in the willows"
    And format as "epub"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title


  Scenario: Individual field search with default sort and format filter
    Given We search on individual parameters
    And title as "the wind in the willows"
    And format as "epub"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title


  Scenario: Individual field search with default sort and paging
    Given We search on individual parameters
    And title as "the wind in the willows"
    And size as "5"
    When we retrieve 5 relevance sorted pages
    Then we get success codes
    And the first 3 results contain "wind in the willows" in the title


  Scenario: Quick search date default sort with paging
    Given We quick search for "the wind in the willows"
    And size as "5"
    When we retrieve 5 relevance sorted pages
    Then we get success codes
    And the first 3 results contain "wind in the willows" in the title
