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

The full procedure (including CLI and REST invocation) lives in the per-language README — see [`typescript/README.md`](typescript/README.md#publishing-a-release).

## CI secrets

| Secret                   | Used by                            | Purpose                                          |
|--------------------------|------------------------------------|--------------------------------------------------|
| `REPO_TYPEDB_TOKEN`      | `deploy-typescript-snapshot.yml`   | Cloudsmith npm publish auth (snapshots)          |
| `REPO_NPM_TOKEN`         | `deploy-typescript-release.yml`    | npmjs.org publish auth (releases)                |
| `GITHUB_TOKEN`           | `deploy-typescript-release.yml`    | Auto-provided by GH Actions; pushes tag + creates Release |
