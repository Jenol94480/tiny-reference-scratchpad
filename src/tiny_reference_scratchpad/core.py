import re
from typing import Optional

# Pre-compile the regex once at import time. Doing this at module scope
# (rather than inside the function) means repeated calls reuse the compiled
# pattern, which matters when decode() is called on many short strings.
#
# The pattern matches both XML numeric character reference forms:
#   &#1639;   decimal form, CharRef ::= '&#' [0-9]+ ';'
#   &#x6A9;   hex form,     CharRef ::= '&#x' [0-9a-fA-F]+ ';'
#
# The 'x' is checked case-insensitively because real-world XML often
# contains &#X...; in lowercase, and being strict there adds no value.
#
# We do NOT use re.IGNORECASE on the whole pattern: the decimal branch
# must not match hex digits like 'a'. Keeping the flags scoped per-group
# would be possible, but the clean approach is two named alternations.
_REF_RE = re.compile(
    r"&(?:"
    r"#(?P<dec>[0-9]+)"
    r"|#[xX](?P<hex>[0-9a-fA-F]+)"
    r");"
)

# XML 1.0 places characters in the range [#x1-#xD7FF | #xE000-#xFFFD |
# #x10000-#x10FFFF] as valid document characters, excluding surrogates
# (#xD800-#xDFFF) and specific restricted code points. For a decoder
# operating on already-parsed content, the pragmatic line is to reject
# surrogates and the non-character C0 control set, and let anything
# representable in Python's str through.
#
# We do NOT attempt full XML Char production validation here. Doing so
# would require encoding the full table (including the obscure
# #x7F-#x84F gap and the last-two-code-points rule for each plane).
# That is beyond the scope of this scratchpad and would trade a clear,
# predictable contract for a brittle one.
_SURROGATE_RANGE = range(0xD800, 0xE000)


def _is_surrogate(code_point: int) -> bool:
    return code_point in _SURROGATE_RANGE


def decode_reference(match: re.Match) -> str:
    """Decode a single regex match of an XML numeric character reference.

    Returns the decoded character as a one-element str, or raises
    ValueError for surrogate code points or empty references.

    A separate function is kept rather than inlining the logic into the
    re.sub callback so it can be unit-tested directly without going
    through the regex layer.
    """
    dec = match.group("dec")
    if dec is not None:
        # Decimal form: straightforward int parse, no base conversion.
        code_point = int(dec)
    else:
        # Hex form. int(..., 16) accepts both uppercase and lowercase,
        # and is robust to leading zeros, which XML permits.
        hex_digits = match.group("hex")
        code_point = int(hex_digits, 16)

    if _is_surrogate(code_point):
        raise ValueError(
            f"XML character reference &#x{code_point:X}; is a "
            "surrogate and cannot be represented directly"
        )

    if code_point == 0:
        raise ValueError("XML character reference &#0; is not permitted")

    return chr(code_point)


def decode(text: Optional[str]) -> str:
    """Decode all XML numeric character references in `text`.

    Handles both decimal (&#1639;) and hexadecimal (&#x6A9; / &#X6A9;)
    forms per XML 1.0. Named entities like &amp; are left untouched.

    Raises ValueError if the input contains a surrogate code point
    reference (e.g. &#xD800;) or &#0;.

    Returns the input unchanged if no references are present. A None
    input is treated as an empty string for caller convenience — this
    is the one non-obvious decision, chosen because callers frequently
    pass through optional fields from JSON or XML maps.
    """
    if text is None:
        return ""
    return _REF_RE.sub(decode_reference, text)
