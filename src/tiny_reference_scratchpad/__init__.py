# tiny_reference_scratchpad
# XML character reference decoder.
#
# Expose the public API at the package root so callers can write:
#     from tiny_reference_scratchpad import decode
#
# Keeping __init__ thin avoids pulling unrelated symbols into the
# public namespace by accident.
from .core import decode, decode_reference

__all__ = ["decode", "decode_reference"]
