#!/usr/bin/env node
// Fails if typescript/package.json's version field disagrees with typescript/VERSION.
//
// Usage: node tool/verify-version.js
//
// VERSION is the source of truth for releases. package.json is allowed to
// drift during development for local builds and dependency tooling, but
// must match VERSION at release time.

const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
const expected = fs.readFileSync(path.join(root, "VERSION"), "utf8").trim();

if (!expected) {
    console.error("ERROR: typescript/VERSION is empty.");
    process.exit(1);
}

if (pkg.version !== expected) {
    console.error(`ERROR: package.json version '${pkg.version}' does not match VERSION '${expected}'.`);
    console.error("       Run: node tool/set-version.js " + expected);
    process.exit(1);
}

console.log(`package.json and VERSION agree on '${expected}'.`);
