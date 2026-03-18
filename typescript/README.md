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
