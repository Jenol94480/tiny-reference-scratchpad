import unittest

from tiny_reference_scratchpad import decode, decode_reference
import re

from tiny_reference_scratchpad.core import _REF_RE


class TestDecode(unittest.TestCase):
    def test_decimal_reference(self):
        self.assertEqual(decode("&#65;"), "A")

    def test_hex_lowercase(self):
        self.assertEqual(decode("&#x6a9;"), "ک")

    def test_hex_uppercase_x_prefix(self):
        # XML spec uses lowercase &#x, but being case-insensitive on the
        # 'x' is harmless and robust to real-world input.
        self.assertEqual(decode("&#X6A9;"), "ک")

    def test_hex_uppercase_digits(self):
        self.assertEqual(decode("&#x6A9;"), "ک")

    def test_mixed_decimal_and_hex_in_one_string(self):
        self.assertEqual(decode("&#65;&#x42;"), "AB")

    def test_reference_with_surrounding_text(self):
        self.assertEqual(decode("hello &#x41; world"), "hello A world")

    def test_no_references_returns_unchanged(self):
        original = "plain text with &amp; named entity"
        self.assertEqual(decode(original), original)

    def test_empty_string(self):
        self.assertEqual(decode(""), "")

    def test_none_input_returns_empty_string(self):
        # Documented non-obvious decision: None -> "" rather than raising.
        self.assertEqual(decode(None), "")

    def test_multiple_references_consecutive(self):
        self.assertEqual(decode("&#72;&#101;&#108;&#108;&#111;"), "Hello")

    def test_reference_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            decode("&#0;")

    def test_surrogate_code_point_raises_value_error(self):
        with self.assertRaises(ValueError):
            decode("&#xD800;")

    def test_surrogate_high_decimal_raises_value_error(self):
        with self.assertRaises(ValueError):
            decode("&#55296;")


class TestDecodeReferenceDirect(unittest.TestCase):
    """Exercise decode_reference through a real regex match object.

    This validates the callback's behaviour without depending on the
    full-string decode path, which is useful for catching off-by-one or
    group-naming regressions.
    """

    def _match(self, ref: str) -> re.Match:
        m = _REF_RE.match(ref)
        self.assertIsNotNone(m, f"reference {ref!r} did not match the regex")
        return m

    def test_decimal_callback(self):
        m = self._match("&#65;")
        self.assertEqual(decode_reference(m), "A")

    def test_hex_callback(self):
        m = self._match("&#x6a9;")
        self.assertEqual(decode_reference(m), "ک")

    def test_leading_zero_decimal(self):
        m = self._match("&#0065;")
        self.assertEqual(decode_reference(m), "A")

    def test_leading_zero_hex(self):
        m = self._match("&#x041;")
        self.assertEqual(decode_reference(m), "A")

    def test_maximum_code_point(self):
        # XML's maximum code point is 0x10FFFF. chr should handle it.
        m = self._match("&#x10FFFF;")
        self.assertEqual(decode_reference(m), chr(0x10FFFF))


if __name__ == "__main__":
    unittest.main()
