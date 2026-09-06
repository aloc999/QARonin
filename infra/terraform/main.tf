# Local-only ephemeral QA environment description.
# Writes a rendered env-manifest.json so CI can advertise where each
# framework should point (BASE_URL) without hardcoding IPs.

resource "random_id" "env" {
  byte_length = 4
}

resource "local_file" "env_manifest" {
  filename = "${path.module}/env-manifest.json"
  content = jsonencode({
    project     = var.project
    environment = var.environment
    suffix      = random_id.env.hex
    target      = { port = var.target_port, health_path = "/api/health" }
    reports     = { junit_glob = "**/junit.xml", visual_report = "reports/visual-report.html" }
  })
}

resource "null_resource" "smoke_gate" {
  triggers = {
    manifest_sha = local_file.env_manifest.content_sha256
  }

  provisioner "local-exec" {
    command = "echo '[qaronin] ephemeral env ${var.environment}-${random_id.env.hex} manifest written to env-manifest.json'"
  }
}
