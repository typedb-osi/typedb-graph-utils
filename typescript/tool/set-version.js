#!/usr/bin/env node
// Sets the version field in typescript/package.json.
//
// Usage: node tool/set-version.js <version>
//
// CI invokes this immediately before `pnpm publish` (snapshot or release).
// During normal development package.json may drift from VERSION; alignment
// is enforced at release time by tool/validate-version.js.

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
