# btclib-org

Bitcoin cryptography in Python, written to be read.

[btclib](https://btclib.org) began as a teaching tool for Ferdinando
Ametrano's *[Bitcoin and Blockchain
Technology](https://www.ametrano.net/bbt/)* course — taught at the
University of Milano-Bicocca, Politecnico di Milano and the University of
Milano — and is used in production today. It is still marked beta,
because it is still refactored whenever that makes it clearer.

What the projects here have in common is a preference for the explicit
one: annotated types everywhere, a public function that validates what it
is handed, and a docstring that states the contract rather than restating
the name. Where behaviour comes from a BIP, an RFC or a Bitcoin Core
function, the code says so and cites it; where these libraries deviate,
they say that too.

## The libraries

- **[btclib](https://github.com/btclib-org/btclib)** — elliptic curve
  cryptography and bitcoin's blockchain, from modular arithmetic up
  through ECDSA, BIP340 Schnorr, BIP32 keys, BIP39 and SLIP39 mnemonics,
  addresses, scripts, transactions, PSBT and output descriptors. Not
  limited to secp256k1: the curve arithmetic serves SEC, NIST, Brainpool
  and low-cardinality test curves alike.
- **[btclib-secp256k1](https://github.com/btclib-org/btclib-secp256k1)**
  — cffi bindings to
  [libsecp256k1](https://github.com/bitcoin-core/secp256k1), Bitcoin
  Core's optimized C library. btclib delegates to them for secp256k1 and
  validates its own Python arithmetic against them: consensus code is
  what says the right answer.
- **[bitcoin-core-rpc](https://github.com/btclib-org/bitcoin-core-rpc)**
  — a standalone JSON-RPC client for a Bitcoin Core node. One source
  file, nothing but the standard library behind it, annotated and
  shipping `py.typed`. Vendoring it is a supported way to use it rather
  than a fallback.
- **[btclib-benchmarks](https://github.com/btclib-org/btclib-benchmarks)**
  — timings against the packages these are usefully compared with. Its
  own repository on purpose: the comparands are third-party libraries,
  and measuring them from inside btclib would put them in the lock file
  of a library that never imports them.

## Around them

- **[btclib_node](https://github.com/btclib-org/btclib_node)** — a
  bitcoin node, consensus and network code in Python, built on btclib.
  Its author reports it downloading and validating the whole chain.
- **[bbt](https://github.com/btclib-org/bbt)** — the course the library
  came out of: slides, spreadsheets illustrating finite fields and
  elliptic curves, notebooks, scripts, and a regtest lab.
- **[portanode](https://github.com/btclib-org/portanode)** — Bitcoin Core
  and Electrum on a portable external disk, shared between macOS and
  Windows.

## Answering to somebody else's vectors

A test suite that only agrees with itself proves that the code does what
it does. These libraries answer to vectors their authors published: the
BIPs' and the SLIPs' own, Bitcoin Core's script, transaction, sighash and
key-encoding files, HWI's, Trezor's for BIP39 and SLIP39, and Appendix
A.2 of RFC 6979. Each vendored file is pinned to the upstream commit it
was copied from, with a monthly job asking whether the two still agree.

Coverage is gated at 100%, so a line no test reaches is a red build
rather than a number that drifts down. Everything
else the repositories here are held to — one lint gate that CI runs
verbatim, strict type checking, signed commits, one commit per pull
request — is written down, with the reasoning and the rejected
alternatives, in
[the repository standard](https://github.com/btclib-org/.github).

## Elsewhere

- the documentation, at [btclib.readthedocs.io](https://btclib.readthedocs.io)
- the packages, on PyPI: [btclib](https://pypi.org/project/btclib/),
  [btclib_secp256k1](https://pypi.org/project/btclib_secp256k1/),
  [bitcoin-core-rpc](https://pypi.org/project/bitcoin-core-rpc/)
- questions and patches: the issues and pull requests of each repository

Everything here is MIT licensed.
