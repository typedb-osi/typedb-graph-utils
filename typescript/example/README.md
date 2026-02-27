# Example: Sigma.js visualiser
A browser-based demo that runs TypeQL queries against TypeDB and visualises the results as a graph using [Sigma.js](https://www.sigmajs.org/).

## Setup
```shell
pnpm install
pnpm run build
```

## Usage
1. Open `query.html` in a browser.
2. Enter your TypeDB server URL, credentials, and database name.
3. Sign in, write a query, and click **Run query**.

The results are shown in two tabs:
- **DataConstraints** — the raw `DataGraph` JSON.
- **Graph** — an interactive Sigma.js visualisation.
