// Copyright (c) The btclib developers
// Distributed under the MIT software license, see the accompanying
// LICENSE file or https://opensource.org/license/mit for the full text.

// Render profile/dependencies.dot into profile/dependencies.svg, or with
// --check refuse an SVG that is not what the source renders to.
//
// The renderer is Graphviz compiled to WebAssembly, the npm package
// @hpcc-js/wasm-graphviz at the version .pre-commit-config.yaml pins for
// the two hooks that run this. One build of the layout engine runs on
// every machine, so the committed SVG is compared byte for byte. The
// `dot` a system package manager installs was the alternative: it is
// whatever release that platform ships, and two releases lay the same
// source out differently, so a byte comparison would hold only on the
// machine that rendered the file.
//
// The package is found through NODE_PATH, which pre-commit sets to the
// hook environment's modules: `import` does not read that variable and
// `require.resolve` does. Run from the repository root, as pre-commit
// runs it.

import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const SOURCE = "profile/dependencies.dot";
const TARGET = "profile/dependencies.svg";
const REGENERATE =
    "uv run --locked --only-group lint pre-commit run --all-files " +
    "--hook-stage manual render-dependencies";

const require = createRequire(import.meta.url);
const { Graphviz } = await import(
    pathToFileURL(require.resolve("@hpcc-js/wasm-graphviz")).href
);

const graphviz = await Graphviz.load();
const rendered = graphviz.dot(readFileSync(SOURCE, "utf8"));

if (process.argv.includes("--check")) {
    let committed = null;
    try {
        committed = readFileSync(TARGET, "utf8");
    } catch {
        // absent, which the comparison below reports as a difference
    }
    if (committed !== rendered) {
        console.error(
            `${TARGET} is not what ${SOURCE} renders to. ` +
                `Regenerate it with:\n\n    ${REGENERATE}\n`,
        );
        process.exit(1);
    }
} else {
    writeFileSync(TARGET, rendered);
}
