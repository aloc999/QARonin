Feature: Orders and RBAC
  Checkout flows mirror AutomationExercise cases 12-17

  Scenario: Add two products and verify the total (AE-12)
    Given I am logged in as "demo"
    When I order 1 unit each of the first 2 products
    Then the order total equals the sum of their prices

  Scenario: Quantity is honored in the total (AE-13)
    Given I am logged in as "demo"
    When I order 4 units of the first product
    Then the order total equals 4 times its price

  Scenario: Ordering an unknown product fails (AE-17)
    Given I am logged in as "demo"
    When I order product 99999
    Then the response status is 404

  Scenario: Users cannot read admin orders
    Given I am logged in as "demo"
    When I list all orders as admin
    Then the response status is 403

  Scenario: Admins can list all orders
    Given I am logged in as "admin"
    When I list all orders as admin
    Then the order count is a number
