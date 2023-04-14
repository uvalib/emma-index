Feature: Non-default sort tests

  Scenario Outline: Quick search with sort
    Given We quick search for "<title>"
    And we sort by <sort_parameter>
    When we execute the search
    Then we get a success code
    And results are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Stand               | title               |

  Scenario Outline: Individual field search with sort
    Given We search on individual parameters
    And title as "<title>"
    And we sort by <sort_parameter>
    When we execute the search
    Then we get a success code
    And results are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Wind in the Willows | publicationDate     |
      | The Stand               | title               |

  Scenario Outline: Quick search with sort and format filter
    Given We quick search for "<title>"
    And format as "epub"
    And we sort by <sort_parameter>
    When we execute the search
    Then we get a success code
    And results are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Wind in the Willows | publicationDate     |
      | The Stand               | title               |

  Scenario Outline: Individual field search with sort and format filter
    Given We search on individual parameters
    And title as "<title>"
    And format as "epub"
    And we sort by <sort_parameter>
    When we execute the search
    Then we get a success code
    And results are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Wind in the Willows | publicationDate     |
      | The Stand               | title               |

  Scenario Outline: Individual field search with sort and paging
    Given We search on individual parameters
    And title as "<title>"
    And sort as "<sort_parameter>"
    And size as "5"
    When we retrieve 5 pages
    Then we get success codes
    And pages are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Wind in the Willows | publicationDate     |
      | The Stand               | title               |

  Scenario Outline: Quick search date sort with paging
    Given We quick search for "<title>"
    And sort as "<sort_parameter>"
    And size as "5"
    When we retrieve 5 pages
    Then we get success codes
    And pages are sorted in <sort_parameter> order
    Examples:
      | title                   | sort_parameter      |
      | The Wind in the Willows | title               |
      | The Wind in the Willows | sortDate            |
      | The Wind in the Willows | lastRemediationDate |
      | The Wind in the Willows | publicationDate     |
      | The Stand               | title               |
