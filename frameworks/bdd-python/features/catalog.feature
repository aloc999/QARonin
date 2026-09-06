Feature: Product catalog
  Product browsing mirrors AutomationExercise cases 8-9

  Scenario: Product list shows the seeded catalog (AE-8)
    When I list products
    Then at least 1 product is returned
    And every product has a name, price and stock

  Scenario: Product detail shows name, price and stock (AE-8)
    Given a product exists
    When I fetch that product by id
    Then the detail contains name, price and stock

  Scenario: Unknown product returns 404 (AE-8 negative)
    When I fetch product 99999
    Then the response status is 404
