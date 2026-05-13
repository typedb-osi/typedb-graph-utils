# AGENTS.md

Conventions for AI agents and contributors working in this repository. For the procedure to publish a release, see the per-language README; this file documents the rules and rationale.

## Repository layout

Two independently-released packages live as siblings:

- `typescript/` — `@typedb/graph-utils` on npm. See [`typescript/README.md`](typescript/README.md).
- `python/` — `typedb-graph-utils` on PyPI. See [`python/README.md`](python/README.md).

They evolve and release on their own cadence. The version numbers do not need to match.

## Versioning

Each language directory owns its version:

- `typescript/VERSION` — source of truth for the npm package version.
- `python/VERSION` — source of truth for the PyPI package version (when added).

There is intentionally no root `VERSION` file.

### TypeScript

- `typescript/VERSION` is the source of truth for releases.
- `typescript/package.json`'s `version` field is allowed to drift from `VERSION` during development. The release workflow runs [`tool/validate-version.js`](typescript/tool/validate-version.js) and refuses to publish if VERSION and package.json disagree, the release tag already exists, or the version is already on npm.
- Use [`tool/set-version.js`](typescript/tool/set-version.js) to update `package.json` — e.g. `node tool/set-version.js 3.7.0`. The snapshot workflow uses the same script to stamp a snapshot-specific version (`0.0.0-<commit-sha>`).

## Releasing

Releases are triggered manually from the GitHub Actions **Run workflow** button (or via `gh`/REST). There is no tag-push or branch-push trigger. Tags are *created by* the workflow after a successful publish; do not create them manually.

Tag format: `typescript-3.7.0`, `python-3.7.0` — no `v` prefix; mirrors the convention used in typedb-driver, typedb, typedb-studio.

### Releasing TypeScript

1. Open a PR that bumps both [`typescript/VERSION`](typescript/VERSION) and [`typescript/package.json`](typescript/package.json) to the new version, and updates [`typescript/RELEASE_NOTES_LATEST.md`](typescript/RELEASE_NOTES_LATEST.md). Run `node tool/set-version.js <new-version>` from `typescript/` to keep the two version fields in sync.
2. Merge the PR to `master`.
3. Trigger the **Deploy TypeScript release** workflow on `master`.

The workflow will:
- run [`tool/validate-version.js`](typescript/tool/validate-version.js) to confirm `VERSION` and `package.json` agree, the release tag is available, and the version is not on npm
- build, test, then `pnpm publish` to npmjs.org
- create and push the `typescript-<VERSION>` tag
- create a GitHub Release with `RELEASE_NOTES_LATEST.md` as the body

#### Triggering the workflow

**GitHub UI:** Actions → **Deploy TypeScript release** → **Run workflow** → pick branch `master` → click **Run workflow**. A `dry_run` checkbox is available; when checked, the workflow builds and runs `pnpm publish --dry-run` (which validates auth and prints the publish notice without uploading) and skips the tag push and GitHub Release.

**GitHub CLI** (`gh auth login` with the `workflow` scope):
```shell
gh workflow run deploy-typescript-release.yml --ref master
gh workflow run deploy-typescript-release.yml --ref master -f dry_run=true
```

**REST API** (token needs `actions: write` and `contents: write`):
```shell
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/typedb-osi/typedb-graph-utils/actions/workflows/deploy-typescript-release.yml/dispatches \
  -d '{"ref":"master","inputs":{"dry_run":"false"}}'
```

## CI secrets

| Secret                   | Used by                            | Purpose                                          |
|--------------------------|------------------------------------|--------------------------------------------------|
| `REPO_TYPEDB_TOKEN`      | `deploy-typescript-snapshot.yml`   | Cloudsmith npm publish auth (snapshots)          |
| `REPO_NPM_TOKEN`         | `deploy-typescript-release.yml`    | npmjs.org publish auth (releases)                |
| `GITHUB_TOKEN`           | `deploy-typescript-release.yml`    | Auto-provided by GH Actions; pushes tag + creates Release |
