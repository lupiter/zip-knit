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
            fake_data = bytes([0] * 1024)  # Match sector_size
            tmp.write(fake_data)
            tmp.flush()
            file = DiskSector(tmp.name)
            self.assertEqual(file.data, fake_data)

    def test_format(self):
        """Test formatting a disk sector resets data and id"""
        with tempfile.NamedTemporaryFile() as tmp:
            fake_data = bytes([1] * 1024)  # Match sector_size
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Format the disk
            disk.format()

            # Verify data is zeroed out
            self.assertEqual(disk.data, bytes([0] * 1024))

            # Verify ID is zeroed out 
            self.assertEqual(disk.get_sector_id(), bytes([0] * 12))  # Match id_size

    def test_write_data_file(self):
        """Test writing data to disk"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector with correct sector size
            fake_data = bytes([0] * 1024)  # Match sector_size
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Write new data
            new_data = bytes([1] * 1024)  # Match sector_size
            disk.data = new_data
            disk.write_data_file()

            # Verify data was updated
            self.assertEqual(disk.data, new_data)

            # Verify data was written to disk
            with open(tmp.name + ".dat", 'rb') as f:  # Add .dat extension
                disk_data = f.read()
                self.assertEqual(disk_data, new_data)

    def test_write_id_file(self):
        """Test writing ID to disk"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Write new ID
            new_id = bytes([2] * 4)
            disk.id = new_id
            disk.write_id_file()

    def test_read_valid_length(self):
        """Test reading with valid sector size"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector with correct sector size
            fake_data = bytes([0] * 1024)  # Match sector_size
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Read data
            data = disk.data
            self.assertEqual(data, fake_data)

    def test_read_invalid_length(self):
        """Test reading with invalid sector size raises error"""
        with tempfile.NamedTemporaryFile() as tmp:
            disk = DiskSector(tmp.name)
            with self.assertRaises(OSError):  # Match actual exception
                disk.read(33)  # Any non-1024 size

    def test_write_valid_length(self):
        """Test writing with valid sector size"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Write data
            new_data = bytes([1] * len(fake_data))
            disk.data = new_data
            disk.write_data_file()

            # Verify data was updated
            self.assertEqual(disk.data, new_data)

    def test_write_invalid_length(self):
        """Test writing with invalid sector size raises error"""
        with tempfile.NamedTemporaryFile() as tmp:
            disk = DiskSector(tmp.name)
            with self.assertRaises(IOError):  # DiskSector.write() raises IOError
                disk.write(bytes([1] * 33))  # Any non-1024 size

    def test_get_sector_id(self): 
        """Test getting sector ID"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector
            fake_data = bytes([0] * 1024)  # Match sector_size
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Test get_sector_id() returns correct ID
            self.assertEqual(disk.get_sector_id(), bytes([0] * 12))  # Match id_size

    def test_set_sector_id_empty(self):
        """Test setting empty sector ID"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Test set_sector_id() with empty ID creates zero-filled ID
            disk.id = bytes([0] * 4)
            disk.write_id_file()

            # Verify ID was updated
            self.assertEqual(disk.get_sector_id(), bytes([0] * 4))

    def test_set_sector_id_valid(self):
        """Test setting valid sector ID"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Create test disk sector
            fake_data = bytes(range(32))
            tmp.write(fake_data)
            tmp.flush()
            disk = DiskSector(tmp.name)

            # Test set_sector_id() with valid ID length
            disk.id = bytes([1] * 4)
            disk.write_id_file()

            # Verify ID was updated
            self.assertEqual(disk.get_sector_id(), bytes([1] * 4))

    def test_set_sector_id_invalid(self):
        """Test setting invalid sector ID raises error"""
        with tempfile.NamedTemporaryFile() as tmp:
            disk = DiskSector(tmp.name)
            with self.assertRaises(OSError):  # Match actual exception
                disk.set_sector_id(bytes([1] * 13))  # Any non-12 size
