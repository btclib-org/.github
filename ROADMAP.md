# Roadmap

What the [btclib-org](https://github.com/btclib-org) organization intends
to do, and what it has decided not to do. Each line names the issue that
records the intention or the decision; the issue, and not this file, holds
how far the work has gone. How a decision is taken is
[`GOVERNANCE.md`](./GOVERNANCE.md).

This roadmap covers the period until 2027-09-30 and is reviewed every
September. Its entries carry no dates, because they state intentions and
not deadlines.

## Maintained as it is

- **`bbt`** is maintained as it is: fixes, dependency updates and the
  organization's standards, with no new features planned, a default under
  review in btclib-org/.github#1330.
- **`bitcoin-core-rpc`** is maintained as it is: fixes, dependency
  updates and the organization's standards, with no new features planned,
  a default under review in btclib-org/.github#1330.
- **`btclib-benchmarks`** is maintained as it is: fixes, dependency
  updates and the organization's standards, with no new features planned,
  a default under review in btclib-org/.github#1330.
- **`btclib-org.github.io`** is maintained as it is: fixes, dependency
  updates and the organization's standards, with no new features planned,
  a default under review in btclib-org/.github#1330.
- **`portanode`** is maintained as it is: fixes, dependency updates and
  the organization's standards, with no new features planned, a default
  under review in btclib-org/.github#1330.

## Intended

- **`btclib` splits along Bitcoin Core's line between consensus and
  wallet** (btclib-org/btclib#2129). `btclib-wallet` takes the wallet
  side, `mnemonic-codes` the mnemonic schemes up to the seed, and
  `ellipticcurves` `curves/` and the parts of `ecc/` the issue does not
  keep in `btclib`, which stays the protocol package a node consumes. The
  issue holds the steps, in that order, and what each is done when.
- **tf2, one conformance suite for any bitcoin node**
  (btclib-org/btclib#2220): Bitcoin Core's functional tests rewritten on
  `btclib`, in a repository of its own, reaching a node only through a
  process it starts and the node's RPC and p2p sockets, with `bitcoind`
  as the reference and `btclib-node` the first target.
- **FROST key generation in `ecc/`**, a trusted-dealer split and then
  ChillDKG, once BIP445 and the ChillDKG draft settle
  (btclib-org/btclib#2200).
- **A Bulletproofs++ range proof in `ecc/`**, beside the Borromean one,
  following secp256k1-zkp's `bppp` module as it lands upstream
  (btclib-org/btclib#1908).
- **The review bot runs again in every repository** that carries
  `claude-review.yml`, at the end of the campaign that switched it off
  (btclib-org/.github#452).
- **Silver at bestpractices.dev** for the repositories section 10's
  `scorecard` entry names (btclib-org/.github#1321).

## Not intended

- **Edwards curves and BLS signatures in `btclib`**
  (btclib-org/btclib#191, btclib-org/btclib#192): no bitcoin consensus
  rule, BIP, address format, descriptor, PSBT field or script uses them.
- **A binding to `sipa/miniscript`** (btclib-org/btclib#508), and **an
  in-process HWI adapter** beside the subprocess one
  (btclib-org/btclib#469).
- **A further split of `btclib`** once `ellipticcurves` has left it, and a
  package of their own for the codecs, the hashes, `p2p` or the shared
  substrate (btclib-org/btclib#2129).
- **A cipher of `btclib`'s own, and code in `btclib` or `btclib-node`
  written for tf2 alone** (btclib-org/btclib#2220).
- **A pinned toolchain for the macOS and Windows wheels of
  `btclib-secp256k1`** (btclib-org/btclib-secp256k1#554): section 12's
  *The compiled wheels are outside that property* says why.
- **Removing the maintainer's bypass from the branch rules**, until the
  maintainer decides otherwise (btclib-org/.github#341).
- **Gold at bestpractices.dev**: btclib-org/.github#1321 records the
  criteria this organization cannot answer by writing a document.
