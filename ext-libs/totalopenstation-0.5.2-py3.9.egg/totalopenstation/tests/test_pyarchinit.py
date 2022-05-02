import unittest

from totalopenstation.formats import Feature, Point
from totalopenstation.output.tops_pyarchinit import OutputFormat

class TestPyarchinitOutput(unittest.TestCase):

    def setUp(self):
        self.data = [
            Feature(Point(0.1, 76.3, 56.2),
                    desc='01',
                    point_name='TEST POINT',
                    id=1),
            Feature(Point(0.1, 26.3, 46.2),
                    desc='02',
                    point_name='TEST POINT #2',
                    id=2),
        ]

    def test_output(self):
        self.output = OutputFormat(self.data).process()
        self.assertEqual(self.output.splitlines()[1], '"","","","01","",56.2,0.1,76.3')
