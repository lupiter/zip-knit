import unittest

from pattern.maths import hto, nibbles, roundeven

class TestMaths(unittest.TestCase):

    def test_nibbles(self):
        self.assertEqual(nibbles(0xFF), (0xF, 0xF))

    def test_hto(self):
        self.assertEqual(hto(3, 2, 1), 321)

    def test_roundeven(self):
        self.assertEqual(roundeven(5), 6)
        self.assertEqual(roundeven(4), 4)
        self.assertEqual(roundeven(3), 4)

if __name__ == '__main__':
    unittest.main()
