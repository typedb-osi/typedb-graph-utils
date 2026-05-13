#!/usr/bin/env node
// Sets the version field in typescript/package.json.
//
// Usage: node tool/set-version.js <version>
//
// Used in two places:
//   - The snapshot workflow stamps a `0.0.0-<sha>` version before publishing.
//   - Developers run this locally when bumping VERSION for a release PR, to
//     keep package.json in sync with VERSION.
//
// The release workflow does NOT call this — the tagged commit must already
// have VERSION and package.json aligned. tool/validate-version.js enforces it.

const fs = require("node:fs");
const path = require("node:path");

const [, , newVersion] = process.argv;
if (!newVersion) {
    console.error("Usage: node tool/set-version.js <version>");
    process.exit(2);
}

const pkgPath = path.resolve(__dirname, "..", "package.json");
const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"));
const previous = pkg.version;
pkg.version = newVersion;
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");
console.log(`package.json version: ${previous} -> ${newVersion}`);
