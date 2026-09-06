package qaronin;

import io.gatling.javaapi.core.ScenarioBuilder;
import io.gatling.javaapi.core.Simulation;
import io.gatling.javaapi.http.HttpProtocolBuilder;

import java.time.Duration;

import static io.gatling.javaapi.core.CoreDsl.*;
import static io.gatling.javaapi.http.HttpDsl.*;

/**
 * RoninShop load profile (Java DSL, no Scala toolchain needed):
 * catalog browsing + health gate with p95/success assertions.
 */
public class RoninShopSimulation extends Simulation {

  String baseUrl = System.getenv().getOrDefault("BASE_URL", "http://127.0.0.1:8199");

  HttpProtocolBuilder httpProtocol = http
      .baseUrl(baseUrl)
      .acceptHeader("application/json");

  ScenarioBuilder browse = scenario("Browse catalog")
      .exec(http("list products").get("/api/products").check(status().is(200)))
      .pause(Duration.ofSeconds(1), Duration.ofSeconds(3))
      .exec(http("product detail").get("/api/products/1").check(status().is(200)));

  ScenarioBuilder health = scenario("Health gate")
      .exec(http("health").get("/api/health").check(status().is(200)));

  {
    setUp(
        browse.injectOpen(rampUsers(20).during(Duration.ofSeconds(30))),
        health.injectOpen(atOnceUsers(5))
    ).protocols(httpProtocol).assertions(
        global().responseTime().percentile(95).lt(800),
        global().successfulRequests().percent().gt(99.0)
    );
  }
}
