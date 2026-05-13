#!/usr/bin/env node
// Validates that typescript/ is in a coherent state to release.
//
// Checks:
//   1. typescript/VERSION is a non-empty, valid semver.
//   2. typescript/package.json's version field matches VERSION.
//   3. git tag `typescript-<VERSION>` does not already exist locally.
//   4. @typedb/graph-utils@<VERSION> is not already on npmjs.org.
//
// Usage: node tool/validate-version.js
//
// Intended for the release workflow's validate job and for local pre-release
// dry-runs. Network access required for the npm check.

const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

const root = path.resolve(__dirname, "..");
const VERSION_PATH = path.join(root, "VERSION");
const PACKAGE_JSON_PATH = path.join(root, "package.json");
const PACKAGE_NAME = "@typedb/graph-utils";
const SEMVER_RE = /^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$/;

function fail(message) {
    console.error(`ERROR: ${message}`);
    process.exit(1);
}

const version = fs.readFileSync(VERSION_PATH, "utf8").trim();
if (!version) fail("typescript/VERSION is empty.");
if (!SEMVER_RE.test(version)) fail(`VERSION '${version}' is not a valid semver.`);

const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, "utf8"));
if (pkg.version !== version) {
    console.error(`ERROR: package.json version '${pkg.version}' does not match VERSION '${version}'.`);
    console.error(`       Run: node tool/set-version.js ${version}`);
    process.exit(1);
}

const tag = `typescript-${version}`;
try {
    execFileSync("git", ["rev-parse", "--verify", `refs/tags/${tag}`], { stdio: "ignore" });
    fail(`tag '${tag}' already exists. Bump typescript/VERSION.`);
} catch {
    // git rev-parse exits non-zero when the ref doesn't exist — what we want.
}

try {
    const result = execFileSync("npm", ["view", `${PACKAGE_NAME}@${version}`, "version"], {
        stdio: ["ignore", "pipe", "ignore"],
        encoding: "utf8",
    }).trim();
    if (result) fail(`${PACKAGE_NAME}@${version} is already published to npm.`);
} catch {
    // npm view exits non-zero for a 404 — what we want.
}

console.log(`Release readiness: VERSION='${version}', tag '${tag}' free, ${PACKAGE_NAME}@${version} not on npm.`);
