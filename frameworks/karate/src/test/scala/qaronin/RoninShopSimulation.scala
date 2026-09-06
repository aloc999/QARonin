package qaronin

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class RoninShopSimulation extends Simulation {
  val baseUrl = sys.env.getOrElse("BASE_URL", "http://127.0.0.1:8199")

  val httpProtocol = http
    .baseUrl(baseUrl)
    .acceptHeader("application/json")

  val browse = scenario("Browse catalog")
    .exec(http("list products").get("/api/products").check(status.is(200)))
    .pause(1, 3)
    .exec(http("product detail").get("/api/products/1").check(status.is(200)))

  val health = scenario("Health gate")
    .exec(http("health").get("/api/health").check(status.is(200)))

  setUp(
    browse.inject(rampUsers(20).during(30.seconds)),
    health.inject(atOnceUsers(5))
  ).protocols(httpProtocol)
    .assertions(
      global.responseTime.percentile(95).lt(800),
      global.successfulRequests.percent.gt(99)
    )
}
