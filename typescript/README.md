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

Releases are triggered by pushing a tag of the form `typescript-<VERSION>` (no `v` prefix). The tagged commit must contain matching [`VERSION`](VERSION) and `package.json` versions; the workflow verifies this and refuses to publish otherwise. [`tool/verify-version.js`](tool/verify-version.js) enforces the check.

### Steps

1. Open a PR that bumps [`VERSION`](VERSION), `package.json`, and [`RELEASE_NOTES_LATEST.md`](RELEASE_NOTES_LATEST.md). Run `node tool/set-version.js <new-version>` to keep `VERSION` and `package.json` in sync.
2. Merge the PR to `master`.
3. Create the release tag. This triggers the **Deploy TypeScript release** workflow, which validates the commit, publishes `@typedb/graph-utils@<VERSION>` to npmjs.org, and creates a GitHub Release if one does not already exist.

### Creating the release tag

**GitHub UI** (recommended):
Releases → **Draft a new release** → choose tag `typescript-<VERSION>` → target `master` → title `TypeScript <VERSION>` → paste [`RELEASE_NOTES_LATEST.md`](RELEASE_NOTES_LATEST.md) into the description (or click *Generate release notes* and edit) → **Publish release**. GitHub creates the tag and the GitHub Release in one step; the workflow then publishes to npm.

**GitHub CLI:**
```shell
gh release create typescript-<VERSION> \
  --target master \
  --title "TypeScript <VERSION>" \
  --notes-file typescript/RELEASE_NOTES_LATEST.md
```

**Plain git** (if you want to skip creating a GitHub Release in this step — the workflow will create one for you):
```shell
git checkout master && git pull
git tag typescript-<VERSION>
git push origin typescript-<VERSION>
```

### Retrying a failed publish

If the workflow fails (e.g. transient npm outage), retry from the failed workflow run's page via **Re-run failed jobs**. The run is scoped to the same tag and commit.

## Snapshots

Every push to `master` under `typescript/**` publishes a snapshot to the Cloudsmith npm registry at `https://npm.cloudsmith.io/typedb/public-snapshot/`. The snapshot version is `<VERSION>-<sha7>`. The `Deploy TypeScript snapshot` workflow can also be triggered manually via `workflow_dispatch` (useful for verifying the pipeline from a feature branch).

Consume a snapshot with:
```shell
npm install --registry https://npm.cloudsmith.io/typedb/public-snapshot/ @typedb/graph-utils@<VERSION>-<sha7>
```
