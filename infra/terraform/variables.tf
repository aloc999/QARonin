variable "project" {
  description = "Resource name prefix"
  type        = string
  default     = "qaronin"
}

variable "environment" {
  description = "Deployment environment (ephemeral PR envs: pr-<number>)"
  type        = string
  default     = "ci"
}

variable "target_port" {
  description = "RoninShop demo-target port"
  type        = number
  default     = 8199
}

variable "enable_cloud" {
  description = "When true, create optional cloud resources (needs AWS creds). Default false keeps validate/plan credential-free."
  type        = bool
  default     = false
}

variable "report_bucket_name" {
  description = "S3 bucket for JUnit/visual/coverage reports (only when enable_cloud=true)"
  type        = string
  default     = ""
}
