# Roadmap

What the [btclib-org](https://github.com/btclib-org) organization intends
to do, and what it has decided not to do. Each line names the issue that
records the intention or the decision; the issue, and not this file, holds
how far the work has gone. How a decision is taken is
[`GOVERNANCE.md`](./GOVERNANCE.md).

An entry under *Intended* cites an open issue, and goes once that issue
closes: the work it names is then done or dropped.
`tests/roadmap_test.py` fails on an entry there that cites no issue, or
a closed one.

This roadmap covers the period until 2027-09-30 and is reviewed every
September. Its entries carry no dates, because they state intentions and
not deadlines.

## Maintained

- **`bbt`** is maintained as it is: fixes, dependency updates and the
  organization's standards, with no new features planned
  (btclib-org/.github#1330).
- **`bip39-slip39`** is maintained as it is: fixes, dependency updates
  and the organization's standards, with no new features planned
  (btclib-org/.github#1892).
- **`bitcoin-core-rpc`** follows the RPCs of each Bitcoin Core release
  (btclib-org/.github#1330).
- **`btclib-benchmarks`** is maintained as it is: fixes, dependency
  updates and the organization's standards, with no new features planned
  (btclib-org/.github#1330).
- **`btclib-org.github.io`** is maintained as it is: fixes, dependency
  updates and the organization's standards, with no new features planned
  (btclib-org/.github#1330).
- **`btclib-secp256k1`** follows libsecp256k1's releases, and
  secp256k1-zkp, which cuts none, for the modules it exposes
  (btclib-org/.github#1330).
- **`btclib-wallet`** is maintained: fixes, dependency updates and the
  organization's standards (btclib-org/.github#1892).
- **`ecc`** is maintained: fixes, dependency updates and the
  organization's standards, and the work *Intended* below names
  (btclib-org/.github#1892).
- **`portanode`** is maintained as it is: fixes, dependency updates and
  the organization's standards, with no new features planned
  (btclib-org/.github#1330).

## Intended

`.github`, the organization's standard, changes as its own tracker
decides: an issue there proposes a rule and every repository the rule
reaches takes it up. The entries below that cite btclib-org/.github are
its intentions beyond that.

- **The codecs leave `btclib`** for `base58-bech32`, a package of their
  own that `btclib` is to depend on (btclib-org/btclib#2712).
- **FROST key generation in `ecc`**, a trusted-dealer split and then
  ChillDKG, once BIP445 and the ChillDKG draft settle
  (btclib-org/btclib#2200).
- **A Bulletproofs++ range proof in `ecc`**, beside the Borromean one,
  following secp256k1-zkp's `bppp` module as it lands upstream
  (btclib-org/btclib#1908).
- **Gold at bestpractices.dev** for the repositories section 10's
  `scorecard` entry names (btclib-org/.github#1761).

## Not intended

- **Edwards curves and BLS signatures in `btclib`**
  (btclib-org/btclib#191, btclib-org/btclib#192): no bitcoin consensus
  rule, BIP, address format, descriptor, PSBT field or script uses them.
- **A binding to `sipa/miniscript`** (btclib-org/btclib#508), and **an
  in-process HWI adapter** beside the subprocess one
  (btclib-org/btclib#469).
- **A package of their own for the hashes, `p2p` or the shared
  substrate**, and any split of `btclib` beyond the codecs' under
  *Intended* (btclib-org/btclib#2129).
- **A cipher of `btclib`'s own, and code in `btclib` or `btclib-node`
  written for tf2 (`bitcoin-node-tests`) alone**
  (btclib-org/btclib#2220).
- **A pinned toolchain for the macOS and Windows wheels of
  `btclib-secp256k1`** (btclib-org/btclib-secp256k1#554): section 12's
  *The compiled wheels are outside that property* says why.
- **Removing the maintainer's bypass from the branch rules of the trees
  without the Best Practices badge**, until the maintainer decides
  otherwise (btclib-org/.github#1740).
