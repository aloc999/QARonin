terraform {
  required_version = ">= 1.6.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# Ephemeral QA environments are provisioned per-PR and destroyed after the
# regression run. Cloud resources (S3 report bucket, EC2 runner) are opt-in
# via enable_cloud so `terraform validate/plan` passes with zero credentials.
