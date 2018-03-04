import unittest


class Test(unittest.TestCase):
    def setUp(self):
        print('some text')

    def tearDown(self):
        print('some text')

if __name__ == "__main__":
    unittest.main()
