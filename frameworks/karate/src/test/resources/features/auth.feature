Feature: RoninShop auth contracts

  Background:
    * url baseUrl

  Scenario: login with valid demo credentials returns bearer token
    Given path 'api/auth/login'
    And request { username: 'demo', password: 'demo1234' }
    When method post
    Then status 200
    And match response.token_type == 'bearer'
    And match response.username == 'demo'
    And match response.access_token == '#string'

  Scenario: login with invalid credentials is rejected
    Given path 'api/auth/login'
    And request { username: 'demo', password: 'wrong-password' }
    When method post
    Then status 401
