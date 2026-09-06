output "environment" {
  description = "Fully-qualified ephemeral environment name"
  value       = "${var.project}-${var.environment}-${random_id.env.hex}"
}

output "manifest_path" {
  description = "Path to the rendered environment manifest"
  value       = local_file.env_manifest.filename
}

output "target_port" {
  description = "Port the demo-target listens on"
  value       = var.target_port
}
