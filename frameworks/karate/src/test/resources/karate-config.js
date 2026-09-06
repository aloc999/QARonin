function fn() {
  var baseUrl = karate.properties['karate.baseUrl'] || java.lang.System.getenv('BASE_URL') || 'http://127.0.0.1:8199';
  return { baseUrl: baseUrl };
}
