Feature: Result grouping tests

  Scenario Outline: Search individual field and group on results
    Given We search on individual parameters
    And title as "<title>"
    And group as "<group>"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "<important_words>" in the title

    Examples:
      | title                   | group                   | important_words     |
      | The Wind in the Willows | emma_titleId            | wind in the willows |
      | The Wind in the Willows | emma_repositoryRecordId | wind in the willows |
      | The Stand               | emma_titleId            | stand               |

  Scenario Outline: Search individual field with grouped results and paging
    Given We search on individual parameters
    And title as "<title>"
    And size as "5"
    When we retrieve 5 pages
    Then we get success codes
    Examples:
      | title                   | group                   |
      | The Wind in the Willows | emma_titleId            |
      | The Wind in the Willows | emma_titleId            |
      | The Stand               | emma_repositoryRecordId |

  Scenario Outline: Search individual parameter sorted by title and group on results
    Given We search on individual parameters
    And title as "<title>"
    And group as "<group>"
    And sort as "<sort_parameter>"
    When we execute the search
    Then we get a success code
    And results are sorted in <sort_parameter> order

    Examples:
      | title                   | group                   | sort_parameter      |
      | The Wind in the Willows | emma_titleId            | title               |
      | The Wind in the Willows | emma_repositoryRecordId | sortDate            |
      | The Stand               | emma_titleId            | lastRemediationDate |

  Scenario Outline: Search individual field with sorting and paging and group on results fails
    Given We search on individual parameters
    And title as "<title>"
    And group as "<group>"
    And sort as "<sort_parameter>"
    And size as "2"
    When we retrieve 2 pages
    Then the last page has bad request code
    And the last page has message "The group parameter cannot be used with the searchAfterId parameter."

    Examples:
      | title                   | group                   | sort_parameter |
      | The Wind in the Willows | emma_titleId            | title          |
      | The Stand               | emma_repositoryRecordId | sortDate       |

  Scenario: Quick search and group on results
    Given We quick search for "the wind in the willows"
    And group as "emma_repositoryRecordId"
    When we execute the search
    Then we get a success code
    And the first 3 results contain "wind in the willows" in the title

  Scenario Outline: Quick search grouped with paging
    Given We quick search for "<title>"
    And group as "<group>"
    And size as "5"
    When we retrieve 5 pages
    Then we get success codes
    Examples:
      | title                   | group                   |
      | The Wind in the Willows | emma_titleId            |
      | The Wind in the Willows | emma_titleId            |
      | The Stand               | emma_repositoryRecordId |

  Scenario Outline: Quick search grouped and sorted with paging fails
    Given We quick search for "<title>"
    And sort as "<sort_parameter>"
    And group as "<group>"
    And size as "2"
    When we retrieve 2 pages
    Then the last page has bad request code
    And the last page has message "The group parameter cannot be used with the searchAfterId parameter."
    Examples:
      | title                   | sort_parameter | group                   |
      | The Wind in the Willows | title          | emma_titleId            |
      | The Wind in the Willows | sortDate       | emma_titleId            |
      | The Stand               | title          | emma_repositoryRecordId |
