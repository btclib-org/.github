"""A probe for btclib-org/.github#1642, not for merging.

`MAX_PROTOCOL_MESSAGE_LENGTH` is Bitcoin Core's, from `src/net.h` at
v31.1. `SHA` matches an abbreviated or a full commit sha in lowercase
hex, and nothing else.
"""

import re

MAX_PROTOCOL_MESSAGE_LENGTH = 3 * 1000 * 1000

SHA = re.compile(r"^[0-9a-f]{7,40}$")
