import random
import tempfile
import os


class TestFile():
    _file_size = 1024*1024*2  # 2Mb

    def __init__(self, size=_file_size, debug=False):
        self._temp_file = tempfile.NamedTemporaryFile(delete=False)
        self._full_filename = self._temp_file.name
        self._file_path = os.path.dirname(self._full_filename)
        self._file_name = os.path.basename(self._full_filename)

        if debug:
            print('creating file %s size: %d ' % (self._full_filename, size))

        size_64b = size // 4
        self._temp_file.file.write(bytes(random.randint(0, 2*64) for _ in range(size_64b)))
        self._temp_file.close()

        if debug:
            print('Complete.')

    def print_info(self):
        print("Created temporary file at %s (size %d)" % (self._full_filename, self._file_size))

    @property
    def filename(self):
        return self._file_name

    @property
    def path(self):
        return self._file_path

    @property
    def full_filename(self):
        return self._full_filename


if __name__ == '__main__':
    t = TestFile()