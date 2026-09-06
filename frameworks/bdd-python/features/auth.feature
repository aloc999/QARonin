Feature: Authentication
  As a RoninShop user
  I want to log in and out
  So that my orders are protected

  Scenario: Login with correct credentials (AE-2)
    Given the demo user exists
    When I log in as "demo" with password "demo1234"
    Then the login succeeds with role "user"

  Scenario: Login with incorrect credentials shows an error (AE-3)
    When I log in as "demo" with password "wrong-password"
    Then the login fails with status 401

  Scenario: Authenticated session carries a bearer token (AE-4)
    Given I am logged in as "demo"
    When I request my own profile area with the token
    Then the request is authorized
