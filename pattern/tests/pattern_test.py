import unittest

from pattern.pattern import PatternMetadata


class TestPattern(unittest.TestCase):
    def test_get_memo(self):
        pattern = PatternMetadata(
            number=1,
            stitches=8,
            rows=1,
            memo_offset=8,
            pattern_offset=16,
            pattern_end_offset=32,
            data=list(range(32))
        )
        memo = pattern.get_memo()
        self.assertEqual(memo, b"\x08")

    def test_get_data(self):
        # Test with single row pattern  
        data = PatternMetadata.get_data(stitches=8, rows=1, data=bytes(range(32)), pattern_offset=16)
        self.assertEqual(data, [b"\x00\x00\x00\x00\x01\x00\x00\x00"])  

        # Test with some fake binary data
        fake_data = bytes([
            0xFF, 0xAA, 0x55, 0x00,  # Some common binary patterns
            0xDE, 0xAD, 0xBE, 0xEF,  # "DEADBEEF"
            0x12, 0x34, 0x56, 0x78,  # Counting pattern
            0xF0, 0x0F, 0xCC, 0x33   # More binary patterns
        ])
        data = PatternMetadata.get_data(stitches=4, rows=2, data=fake_data, pattern_offset=0)
        self.assertEqual(data, [
            bytes([1, 1, 1, 1]),  # First row - all bits set from 0xFF
            bytes([1, 1, 1, 1])   # Second row - all bits set from 0xDE
        ])

        # Test with a more complex pattern
        complex_data = bytes([
            0x00, 0x01, 0x02, 0x03,  # Counting pattern
            0x04, 0x05, 0x06, 0x07,  # Counting pattern
            0x08, 0x09, 0x0A, 0x0B,  # Counting pattern
            0x0C, 0x0D, 0x0E, 0x0F,  # Counting pattern
            0x10, 0x11, 0x12, 0x13,  # Counting pattern
            0x14, 0x15, 0x16, 0x17,  # Counting pattern
            0x18, 0x19, 0x1A, 0x1B,  # Counting pattern
            0x1C, 0x1D, 0x1E, 0x1F   # Counting pattern
        ])
        data = PatternMetadata.get_data(stitches=4, rows=4, data=complex_data, pattern_offset=0)
        self.assertEqual(data, [
            bytes([0, 0, 0, 0]),      # First row - bits from first nibble
            bytes([0, 0, 0, 0]),      # Second row - bits from second nibble
            bytes([1, 1, 1, 1]),      # Third row - bits from third nibble  
            bytes([1, 0, 0, 0])       # Fourth row - bits from fourth nibble
        ])
