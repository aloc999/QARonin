# Terraform / IaC

Provisions ephemeral QA environments per PR/nightly run.

- Credential-free by default: `main.tf` uses only `null`/`local`/`random`
  providers, so `terraform init -backend=false && terraform validate` passes
  in CI with no AWS keys.
- `enable_cloud=true` is the extension point for real S3/EC2 report
  infrastructure; keep default `false` in CI.
- `env-manifest.json` (generated, gitignored) tells runners the target port
  and report globs.

```bash
make tf-validate   # init + validate (skips gracefully if terraform missing)
make tf-plan       # validate + plan
```

CI job: `terraform` in ci.yml / regression-30min.yml.
