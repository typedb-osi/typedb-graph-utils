# Example: Sigma.js visualiser
A browser-based demo that runs TypeQL queries against TypeDB and visualises the results as a graph using [Sigma.js](https://www.sigmajs.org/).

## Setup
```shell
pnpm install
pnpm run build
```

## Usage
1. Open `index.html` in a browser.
2. Enter your TypeDB server URL, credentials, and database name.
3. Sign in, write a query, and click **Run query**.

The results are shown in two tabs:
- **DataConstraints** — the raw `DataGraph` JSON.
- **Graph** — an interactive Sigma.js visualisation.

## Learning:
The important interaction with the `typedb-graph-utils` library has been extracted to the `SigmaJSExample` class in [main.ts](main.ts).

[index.html](index.html) contains UI logic, 
calls to the [TypeDB HTTP driver](https://typedb.com/docs/reference/typedb-http-drivers/typescript/),and 
calls to our SigmaJSExample class.
