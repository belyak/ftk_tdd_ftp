import random
import tempfile
import os


class TestFile():

    def __init__(self, size, debug=False):
        self._temp_file = tempfile.NamedTemporaryFile(delete=False)
        self._full_filename = self._temp_file.name
        self._file_path = os.path.dirname(self._full_filename)
        self._file_name = os.path.basename(self._full_filename)

        if debug:
            print('creating file %s size: %d ' % (self._full_filename, size))

        self._temp_file.file.write(bytes(random.randint(0, 255) for _ in range(size)))
        self._temp_file.close()

        self._file_size = size

        if debug:
            print('Complete.')

    def get_content(self):
        with open(self._temp_file.name, 'rb') as f:
            content = f.read()
        return content

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