# tiny-reference-scratchpad

Decodes XML numeric character references (decimal `&#1639;` and hexadecimal `&#x6A9;`) in strings, returning the literal characters they represent.

```python
from tiny_reference_scratchpad import decode

decode("&#65;&#x42;")        # -> "AB"
decode("hello &#x41; world")  # -> "hello A world"
decode("plain &amp; text")    # -> "plain &amp; text" (named entities untouched)
```

This exists because when you scrape, parse, or otherwise handle XML-derived text outside a full XML parser, you frequently end up with strings containing numeric character references that the surrounding tooling did not resolve. Running a full XML parser just to unescape a fragment is overkill; the reference grammar is small and stable enough that a focused decoder is the right trade-off.

The one awkward edge: surrogates (`&#xD800;`–`&#xDFFF;`) and `&#0;` raise `ValueError`. Python's `chr()` would otherwise emit a lone surrogate or a NUL, both of which are not legal XML characters and tend to corrupt downstream text. Anything else in the Unicode range passes through. The decoder deliberately does not attempt full XML 1.0 `Char` production validation — that table is large and brittle, and narrowing the contract to "surrogates and NUL are rejected, everything else is passed through" is more predictable for callers.

`decode(None)` returns `""` rather than raising. This is a convenience for code passing through optional fields.
