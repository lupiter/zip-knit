import os
import tempfile
import unittest
from pathlib import Path

from pddemulate.disk_sector import DiskSector


THIS_DIR = Path(__file__).parent
SAMPLE = os.path.join(THIS_DIR, "file-01.dat.sample")


class TestDiskSector(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(IOError):
            DiskSector("")
        
        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            file = DiskSector(tmp.name)
            self.assertEqual(file.data, fake_data)