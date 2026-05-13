# Graph visualisation with TypeDB (TypeScript)
A utility library to construct graph structures from TypeQL `conceptRows` query results.

## Install
```shell
pnpm install
```

## Build
```shell
pnpm run build
```

## Using the library
The library provides three main exports:

- **`constructGraphFromRowsResult(response)`** — converts a `ConceptRowsQueryResponse` (from `@typedb/driver-http`) into a `DataGraph`, a structured representation of the vertices and constraints in the query result.
- **`TypeDBAnswerConverter`** — an interface you implement to define how each constraint type (e.g. `isa`, `has`, `links`, `sub`) is handled.
- **`convertLogicalGraphWith(dataGraph, converter)`** — walks a `DataGraph` and calls the appropriate method on your converter for each constraint.

### Example usage
```typescript
import { constructGraphFromRowsResult, convertLogicalGraphWith, TypeDBAnswerConverter } from "typedb-visualizer-tutorial";

// 1. Run a query against TypeDB via the HTTP API with includeQueryStructure: true
const response: ConceptRowsQueryResponse = /* ... */;

// 2. Build a DataGraph from the response
const structuredAnswers = new StructuredAnswersBuilder().build(rowsResult);

// 3. Implement TypeDBAnswerConverter and walk the graph
const graphBuilder: AbstractGraphBuilder = /* your implementation */;
graphBuilder.build(dataGraph);
```

A complete working example using Sigma.js for browser visualisation is in [example/](example/).

## Publishing a release

The release pipeline is driven by the [`VERSION`](VERSION) file. `package.json` may drift from `VERSION` during development, but they must agree at release time; [`tool/verify-version.js`](tool/verify-version.js) runs first in the release workflow and fails the run if they don't.

### Steps

1. Open a PR that bumps both [`VERSION`](VERSION) and `package.json` to the new version, and updates [`RELEASE_NOTES_LATEST.md`](RELEASE_NOTES_LATEST.md).
   - To keep them in sync, run `node tool/set-version.js <new-version>` after editing `VERSION`.
2. Merge the PR to `master`.
3. Trigger the **Deploy TypeScript release** workflow on `master`.

The workflow will:
- run [`tool/verify-version.js`](tool/verify-version.js) to confirm `VERSION` and `package.json` agree
- check that the tag `typescript-<VERSION>` doesn't already exist
- check that `@typedb/graph-utils@<VERSION>` isn't already on npm
- check that `RELEASE_NOTES_LATEST.md` is non-empty
- build, test, then `pnpm publish` to npmjs.org
- create and push the `typescript-<VERSION>` tag
- create a GitHub Release with `RELEASE_NOTES_LATEST.md` as the body

### Triggering the workflow

**GitHub UI:** Actions → **Deploy TypeScript release** → **Run workflow** → pick branch `master` → click **Run workflow**. A `dry_run` checkbox is available; when checked, the workflow builds and runs `pnpm publish --dry-run` but skips the npm publish, tag push, and GitHub Release.

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

## Snapshots

Every push to `master` under `typescript/**` publishes a snapshot to the Cloudsmith npm registry at `https://npm.cloudsmith.io/typedb/public-snapshot/`. The snapshot version is `<VERSION>-<sha7>`. The `Deploy TypeScript snapshot` workflow can also be triggered manually via `workflow_dispatch` (useful for verifying the pipeline from a feature branch).

Consume a snapshot with:
```shell
npm install --registry https://npm.cloudsmith.io/typedb/public-snapshot/ @typedb/graph-utils@<VERSION>-<sha7>
```
