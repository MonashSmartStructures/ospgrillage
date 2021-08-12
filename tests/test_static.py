import pytest
import ospgrillage as og
import sys, os
sys.path.insert(0, os.path.abspath('../'))

# test if sort vertice function returns a clockwise
def test_sort_vertices():
    point_list = [og.LoadPoint(x=8, y=0, z=3, p=5), og.LoadPoint(x=8, y=0, z=5, p=5), og.LoadPoint(x=5, y=0, z=3, p=5),
                  og.LoadPoint(x=5, y=0, z=5, p=5)]
    ref_ans = [og.LoadPoint(x=5, y=0, z=3, p=5), og.LoadPoint(x=8, y=0, z=3, p=5),
               og.LoadPoint(x=8, y=0, z=5, p=5), og.LoadPoint(x=5, y=0, z=5, p=5)]
    actual, _ = og.sort_vertices(point_list)
    assert actual == ref_ans
