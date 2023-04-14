Feature: Sort and filter


  Scenario: Quick search with publisher filter
    Given We quick search for "the wind in the willows"
    And publisher as "penguin"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title
    And the first 3 results contain "penguin" in the publisher

  Scenario: Quick search with publisher filter and date sort
    Given We quick search for "the wind in the willows"
    And publisher as "penguin"
    And we sort by sortDate
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title
    And the first 3 results contain "penguin" in the publisher
    And results are sorted in sortDate order

  Scenario: Quick search with publisher filter and date sort
    Given We quick search for "the wind in the willows"
    And publisher as "penguin"
    And we sort by title
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title
    And the first 3 results contain "penguin" in the publisher
    And results are sorted in title order

Scenario: Quick search with publisher filter and date sort
    Given We quick search for "the wind in the willows"
    And publisher as "penguin"
    And we sort by publicationDate
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title
    And the first 3 results contain "penguin" in the publisher
    And results are sorted in publicationDate order


