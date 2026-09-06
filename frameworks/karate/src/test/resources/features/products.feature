Feature: RoninShop product catalog

  Background:
    * url baseUrl

  Scenario: list products returns seeded catalog
    Given path 'api/products'
    When method get
    Then status 200
    And match response == '#array'
    And match response[0] contains { id: '#number', name: '#string', price: '#number', stock: '#number' }

  Scenario: get single product by id
    Given path 'api/products/1'
    When method get
    Then status 200
    And match response.id == 1
    And match response.name == '#string'

  Scenario: unknown product returns 404
    Given path 'api/products/99999'
    When method get
    Then status 404
