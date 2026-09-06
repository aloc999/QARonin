Feature: RoninShop orders + RBAC

  Background:
    * url baseUrl
    Given path 'api/auth/login'
    And request { username: 'demo', password: 'demo1234' }
    When method post
    Then status 200
    * def userToken = response.access_token

    Given path 'api/auth/login'
    And request { username: 'admin', password: 'admin1234' }
    When method post
    Then status 200
    * def adminToken = response.access_token

  Scenario: create order with one item
    Given path 'api/orders'
    And header Authorization = 'Bearer ' + userToken
    And request { items: [{ product_id: 1, quantity: 1 }] }
    When method post
    Then status 201
    And match response.username == 'demo'
    And match response.total == '#number'

  Scenario: user cannot list admin orders
    Given path 'api/admin/orders'
    And header Authorization = 'Bearer ' + userToken
    When method get
    Then status 403

  Scenario: admin can list orders
    Given path 'api/admin/orders'
    And header Authorization = 'Bearer ' + adminToken
    When method get
    Then status 200
    And match response.count == '#number'
