# Branch Protection Checklist (QMS-DC-002)

Solo-maintainer mode: gates block red merges for everyone (including the
owner), but do not require peer approvals — there are no peers yet. When
collaborator #2 joins, flip §4 to required reviews.

## 1. GitHub (`aloc999/QARonin`, branch `main`) — APPLIED via API

- [x] `required_status_checks.strict: true` (PR must be up to date)
- [x] Required contexts (both workflows):
  - ci.yml: `lint`, `target-tests`, `api-tests`, `postman-newman`,
    `playwright-smoke`, `selenium-tests`, `selfheal-tests`, `db-validation`
  - regression-30min.yml: `shard-a-api`, `pact`, `karate`, `shard-b-ts-ui`,
    `csharp-tests`, `terraform`, `coverage`, `cypress-e2e`,
    `bdd-deepeval-mcp`, `ops-tools`, `visual-report`, `budget-gate-30min`
  - NOT required (informational): `zap-baseline` (continue-on-error),
    `perf-extra`, `slack-notify`, nightly-only jobs
- [x] `required_linear_history: true`
- [x] `required_conversation_resolution: true`
- [x] `allow_force_pushes: false`, `allow_deletions: false`
- [x] `enforce_admins: true`
- [ ] `required_pull_request_reviews` — intentionally OFF (solo; would deadlock
      self-merge). Enable with 1 approval when a collaborator joins.

Applied with (verified 2026-09-06: strict + 20 contexts + linear + resolution,
no force/deletion, enforce_admins; use a JSON file, `-f` sends strings):

```bash
python3 -c "import json; open('/tmp/protection.json','w').write(json.dumps({
  'required_status_checks': {'strict': True, 'contexts': [...]},
  'enforce_admins': True, 'required_pull_request_reviews': None,
  'restrictions': None, 'required_linear_history': True,
  'allow_force_pushes': False, 'allow_deletions': False,
  'required_conversation_resolution': True}))"
gh api repos/aloc999/QARonin/branches/main/protection -X PUT --input /tmp/protection.json
```

Verify: `gh api repos/aloc999/QARonin/branches/main/protection --jq .required_status_checks.contexts`.

## 2. GitLab (`aloc999/QARonin`, branch `main`) — TODO after token rotation

GitLab needs a fresh token (the chat-exposed one must be revoked first).

- [ ] Settings → Repository → Protected branches → `main`:
  - Allowed to merge: Maintainers
  - Allowed to push: No one
  - Allowed to force push: OFF
- [ ] Settings → Merge requests → enable:
  - Pipelines must succeed
  - All threads must be resolved
  - No fast-forward merges unchecked? keep default; require linear history equivalent:
    Settings → Repository → Default branch → merge method: Fast-forward
- [ ] Or via API with the NEW token:
```bash
curl --request POST --header "PRIVATE-TOKEN: <NEW_TOKEN>" \
  --data "name=main&push_access_level=0&merge_access_level=40&allow_force_push=false" \
  https://gitlab.com/api/v4/projects/aloc999%2FQARonin/protected_branches
curl --request PUT --header "PRIVATE-TOKEN: <NEW_TOKEN>" \
  --data "only_allow_merge_if_pipeline_succeeds=true&only_allow_merge_if_all_discussions_are_resolved=true" \
  https://gitlab.com/api/v4/projects/aloc999%2FQARonin
```

## 3. Quarterly review

- [ ] Required-context list matches current workflow job names (rename = silent unprotection)
- [ ] Flip §4 reviews ON once a second maintainer exists
- [ ] Confirm no admin bypasses were used without a linked ticket
