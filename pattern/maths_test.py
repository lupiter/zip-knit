import unittest

from pattern.maths import (
    hto,
    nibbles,
    roundeight,
    roundeven,
    roundfour,
    nibbles_per_row,
    bytes_per_pattern,
    bytes_for_memo,
    bytes_per_pattern_and_memo,
)


class TestMaths(unittest.TestCase):

    def test_nibbles(self):
        self.assertEqual(nibbles(0xFF), (0xF, 0xF))

    def test_hto(self):
        self.assertEqual(hto(3, 2, 1), 321)

    def test_roundeven(self):
        self.assertEqual(roundeven(5), 6)
        self.assertEqual(roundeven(4), 4)
        self.assertEqual(roundeven(3), 4)

    def test_roundeight(self):
        self.assertEqual(roundeight(1), 8)
        self.assertEqual(roundeight(7), 8)
        self.assertEqual(roundeight(8), 8)
        self.assertEqual(roundeight(9), 16)
        self.assertEqual(roundeight(15), 16)
        self.assertEqual(roundeight(16), 16)
        self.assertEqual(roundeight(17), 24)

    def test_roundfour(self):
        self.assertEqual(roundfour(1), 4)
        self.assertEqual(roundfour(3), 4)
        self.assertEqual(roundfour(4), 4)
        self.assertEqual(roundfour(5), 8)

    def test_nibbles_per_row(self):
        self.assertEqual(nibbles_per_row(1), 1)
        self.assertEqual(nibbles_per_row(4), 1)
        self.assertEqual(nibbles_per_row(8), 2)
        self.assertEqual(nibbles_per_row(16), 4)
        self.assertEqual(nibbles_per_row(31), 8)
        self.assertEqual(nibbles_per_row(32), 8)
        self.assertEqual(nibbles_per_row(33), 9)

    def test_bytes_per_pattern(self):
        self.assertEqual(bytes_per_pattern(1, 1), 1)
        self.assertEqual(bytes_per_pattern(4, 4), 2)
        self.assertEqual(bytes_per_pattern(16, 16), 32)
        self.assertEqual(bytes_per_pattern(17, 17), 43)
        self.assertEqual(bytes_per_pattern(160, 160), 3200)

    def test_bytes_for_memo(self):
        self.assertEqual(bytes_for_memo(1), 1)
        self.assertEqual(bytes_for_memo(4), 2)
        self.assertEqual(bytes_for_memo(8), 4)
        self.assertEqual(bytes_for_memo(15), 8)
        self.assertEqual(bytes_for_memo(16), 8)
        self.assertEqual(bytes_for_memo(17), 9)
        self.assertEqual(bytes_for_memo(32), 16)

    def test_bytes_per_pattern_and_memo(self):
        self.assertEqual(
            bytes_per_pattern_and_memo(200, 123),
            bytes_per_pattern(200, 123) + bytes_for_memo(123),
        )


if __name__ == "__main__":
    unittest.main()
