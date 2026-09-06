Feature: stateful mock payment gateway + pricing engine

  # Karate's mock server lets UI/API suites run independent of backend
  # readiness. Run: `karate mock-payment.feature` (netty, default :8080),
  # or via the MockRunner in CI. The RoninShop checkout flow points at these
  # doubles with PAYMENTS_BASE_URL.

  Background:
    * def catalog = [{ id: 1, price: 49.99 }, { id: 2, price: 29.50 }]

  Scenario: pathMatches('/mock/pay') && methodIs('post')
    * def body = request
    * def total = 0
    * eval karate.forEach(body.items, function(i){ total += i.price * i.qty })
    * def response = { transactionId: 'txn-' + java.util.UUID.randomUUID(), total: total, status: 'authorized' }

  Scenario: pathMatches('/mock/pricing/{id}') && methodIs('get')
    * def item = karate.filter(catalog, function(p){ return p.id == parseInt(pathParams.id) })[0]
    * def responseStatus = item ? 200 : 404
    * def response = item || { detail: 'priced item not found' }

  Scenario:
    * def responseStatus = 404
    * def response = { detail: 'no mock matched' }
