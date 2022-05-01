import unittest

import pytest

from totalopenstation.formats.topcon_gpt import FormatParser

from . import BaseTestOutput

class TestTopconGPTParser(unittest.TestCase):

    def setUp(self):
        with open('sample_data/topcon_gpt') as testdata:
            self.fp = FormatParser(testdata.read())

    def test_point(self):
        self.assertAlmostEqual(self.fp.points[0].geometry.x, 95.8952)
        self.assertAlmostEqual(self.fp.points[0].geometry.y, 207.8514)
        self.assertAlmostEqual(self.fp.points[0].geometry.z, 60.12)

    def test_feature(self):
        self.assertEqual(self.fp.points[0].id, 'SD')
        self.assertEqual(self.fp.points[0].desc, 'SD')
        self.assertEqual(self.fp.points[1].desc, 'SD')

class TestTopconGTSOutput(BaseTestOutput):

    @pytest.fixture
    def setup(self):
        with open('sample_data/topcon_gpt') as testdata:
            self.fp = FormatParser(testdata.read())
