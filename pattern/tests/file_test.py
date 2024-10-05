import os
import tempfile
import unittest
from pathlib import Path

from pattern.file import BrotherFile


THIS_DIR = Path(__file__).parent
SAMPLE = os.path.join(THIS_DIR, "file-01.dat")


class TestFile(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(IOError):
            BrotherFile("")

        with self.assertRaises(FileNotFoundError):
            with tempfile.NamedTemporaryFile(mode="r") as tmp:
                BrotherFile(tmp.name)

        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            file = BrotherFile(tmp.name)
            self.assertEqual(file.data_file_name, tmp.name)
            self.assertEqual(file.data, fake_data)

    def test_get_indexed_byte(self):
        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            file = BrotherFile(tmp.name)
            self.assertEqual(file.get_indexed_byte(0), fake_data[0])
            self.assertEqual(file.get_indexed_byte(31), fake_data[31])

    def test_set_indexed_byte(self):
        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            file = BrotherFile(tmp.name)
            self.assertEqual(file.data[31], fake_data[31])
            file.set_indexed_byte(31, 0)
            self.assertEqual(file.data[31], 0)
            self.assertNotEqual(file.data[31], fake_data[31])

    def test_get_indexed_nibble(self):
        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            file = BrotherFile(tmp.name)
            self.assertEqual(file.get_indexed_nibble(0, 0), 0)
            self.assertEqual(file.get_indexed_nibble(31, 0), 15)
            self.assertEqual(file.get_indexed_nibble(0, 31), 1)
            self.assertEqual(file.get_indexed_nibble(5, 2), 4)

    def test_get_patterns(self):
        file = BrotherFile(SAMPLE)
        patterns = file.get_patterns()
        self.assertEqual(len(patterns), 2)
        self.assertEqual(patterns[0].number, 0)
        self.assertEqual(patterns[0].stitches, 0)
        self.assertEqual(patterns[0].rows, 0)
        self.assertEqual(patterns[0].memo_offset, -2049)
        self.assertEqual(patterns[0].pattern_offset, -2049)
        self.assertEqual(patterns[0].pattern_end_offset, -2049)
        self.assertEqual(patterns[1].number, 34)
        self.assertEqual(patterns[1].stitches, 10)
        self.assertEqual(patterns[1].rows, 50)
        self.assertEqual(patterns[1].memo_offset, 511)
        self.assertEqual(patterns[1].pattern_offset, 486)
        self.assertEqual(patterns[1].pattern_end_offset, 411)

    def test_get_pattern(self):
        file = BrotherFile(SAMPLE)
        patterns = file.get_patterns()
        first = file.get_pattern(0)
        self.assertEqual(first, patterns[0])
        last = file.get_pattern(34)
        self.assertEqual(last, patterns[1])

    def test_get_pattern_data(self):
        file = BrotherFile(SAMPLE)
        data = file.get_pattern_data(0)
        self.assertEqual(len(data), 0)
        data = file.get_pattern_data(34)
        self.assertEqual(len(data), 50)
        self.assertEqual(len(data[0]), 10)
