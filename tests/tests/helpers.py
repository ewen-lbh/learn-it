import unittest
from src.helpers import *


class StripList(unittest.TestCase):

    def test_normal(self):
        self.assertEqual(strip_list(['', None, '', 'hello', '', 'world', '', False, '']), ['hello', '', 'world'])

    def test_empty_list(self):
        self.assertEqual(strip_list([False, '']), [])
