import unittest

import pytest

from totalopenstation.formats.trimble_dc import FormatParser

from . import BaseTestOutput


class TestTrimbleDCParser(unittest.TestCase):

    def setUp(self):
        with open('sample_data/trimble/cuma.dc') as testdata:
            self.fp = FormatParser(testdata.read())

    def test_point(self):
        self.assertAlmostEqual(self.fp.points[0].geometry.coords[0][1], 4522381.79500000)
        self.assertAlmostEqual(self.fp.points[0].geometry.y, 4522381.79500000)
        self.assertAlmostEqual(self.fp.points[0].geometry.coords[0][0], 2440505.70600000)
        self.assertAlmostEqual(self.fp.points[0].geometry.coords[0][2], 15.5560000000000)

    def test_feature(self):
        self.assertEqual(self.fp.points[0].id, 'CAPIT           ')
        self.assertEqual(self.fp.points[0].desc, 'ctrl1')
        self.assertEqual(self.fp.points[1].desc, 'ctrl2')

    def test_linestring(self):
        self.ls = self.fp.build_linestring()
        self.assertAlmostEqual(self.ls.coords[0][0], 2440505.70600000)


class TestSokkiaOutput(BaseTestOutput):

    @pytest.fixture
    def setup(self):
        with open('sample_data/trimble/cuma.dc') as testdata:
            self.fp = FormatParser(testdata.read())