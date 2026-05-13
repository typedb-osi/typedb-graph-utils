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
- `typescript/package.json`'s `version` field is allowed to drift from `VERSION` during development. The release workflow runs [`tool/verify-version.js`](typescript/tool/verify-version.js) and refuses to publish if the two disagree.
- Use [`tool/set-version.js`](typescript/tool/set-version.js) to update `package.json` — e.g. `node tool/set-version.js 3.7.0`. The snapshot workflow uses the same script to stamp a snapshot-specific version (`<VERSION>-<full-commit-sha>`).

## Releasing

Releases are triggered by pushing a release tag. The tag is the canonical record of a release; the workflow only reacts to it. There is no branch-push trigger.

Tag format: `typescript-3.7.0`, `python-3.7.0` — no `v` prefix; mirrors the convention used in typedb-driver, typedb, typedb-studio.

The tagged commit must contain `VERSION` and `package.json` (or the language-equivalent manifest) at the version named by the tag. The release workflow refuses to publish if they disagree.

If a release run fails transiently (e.g. an npm registry outage), retry it from the failed run's page via **Re-run failed jobs**, not by re-pushing the tag.

The full procedure lives in the per-language README — see [`typescript/README.md`](typescript/README.md#publishing-a-release).

## CI secrets

| Secret                   | Used by                            | Purpose                                          |
|--------------------------|------------------------------------|--------------------------------------------------|
| `REPO_TYPEDB_TOKEN`      | `deploy-typescript-snapshot.yml`   | Cloudsmith npm publish auth (snapshots)          |
| `REPO_NPM_TOKEN`         | `deploy-typescript-release.yml`    | npmjs.org publish auth (releases)                |
| `GITHUB_TOKEN`           | `deploy-typescript-release.yml`    | Auto-provided by GH Actions; creates GitHub Release |
