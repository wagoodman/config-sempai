import os
import shutil
import sys
import tempfile
import unittest

import configsempai

TEST_FILE = '''{
    "three": 3,
    "one": {
        "two": {
            "three": 3
        }
    },
    "array": [
        {"nested": "but dotted"},
        {"array": [
            {"and_nested_again": "dotted"}
        ]}
    ],
    "lots_of_lists": [[{"in_da_list": true}]]
}'''

# TODO: add yaml/xml tests

class TestSempai(unittest.TestCase):

    def setUp(self):
        self.direc = tempfile.mkdtemp(prefix='configsempai')
        sys.path.append(self.direc)

        with open(os.path.join(self.direc, 'sempai.json'), 'w') as f:
            f.write(TEST_FILE)

    def tearDown(self):
        sys.path.remove(self.direc)
        shutil.rmtree(self.direc)

    def test_import(self):
        with configsempai.imports():
            import sempai
        self.assertTrue(sempai is not None)

    def test_access(self):
        with configsempai.imports():
            import sempai
        self.assertEqual(3, sempai.three)

    def test_access_nested(self):
        with configsempai.imports():
            import sempai
        self.assertEqual(3, sempai.one.two.three)

    def test_acts_like_dict(self):
        with configsempai.imports():
            import sempai
        self.assertEqual({"three": 3}, sempai.one.two)

    def test_set(self):
        with configsempai.imports():
            import sempai
        sempai.one.two.three = 4
        self.assertEqual(4, sempai.one.two.three)

    def test_del(self):
        with configsempai.imports():
            import sempai
        del sempai.one.two.three
        self.assertEqual('not at home',
                         sempai.one.two.get('three', 'not at home'))

    def test_location(self):
        del sys.modules['sempai'] # force the module to be reloaded
        with configsempai.imports():
            import sempai
        self.assertEqual(os.path.join(self.direc, 'sempai.json'),
                         sempai.__file__)

    def test_array(self):
        with configsempai.imports():
            import sempai
        self.assertEqual({"nested": "but dotted"},
                         sempai.array[0])
    def test_array_dotting(self):
        with configsempai.imports():
            import sempai
        self.assertEqual('but dotted', sempai.array[0].nested)

    def test_array_nested_dotting(self):
        with configsempai.imports():
            import sempai
        self.assertEqual('dotted', sempai.array[1].array[0].and_nested_again)

    def test_obj_in_list_in_list(self):
        with configsempai.imports():
            import sempai
        self.assertTrue(sempai.lots_of_lists[0][0].in_da_list)

    def test_import_invalid_file(self):
        with open(os.path.join(self.direc, 'invalid.json'), 'w') as f:
            f.write('not a valid json file')

        with configsempai.imports():
            self.assertRaises(ImportError, __import__, 'invalid')


class TestSempaiPackages(unittest.TestCase):

    def setUp(self):
        self.direc = tempfile.mkdtemp(prefix='configsempai')
        sys.path.append(self.direc)

        python_package = os.path.join(self.direc, 'python_package')
        os.makedirs(python_package)

        open(os.path.join(python_package, '__init__.py'), 'w').close()

        with open(os.path.join(python_package, 'nested.json'), 'w') as f:
            f.write(TEST_FILE)

    def tearDown(self):
        sys.path.remove(self.direc)
        shutil.rmtree(self.direc)

    def test_import_from_package(self):
        with configsempai.imports():
            from python_package import nested

        self.assertEqual(3, nested.three)

    def test_import_package(self):
        with configsempai.imports():
            import python_package.nested

        self.assertEqual(3, python_package.nested.three)
