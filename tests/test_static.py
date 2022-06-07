import pytest
import ospgrillage as og
import sys, os

sys.path.insert(0, os.path.abspath("../"))

# test if sort vertice function returns a clockwise
def test_sort_vertices():
    point_list = [
        og.LoadPoint(x=8, y=0, z=3, p=5),
        og.LoadPoint(x=8, y=0, z=5, p=5),
        og.LoadPoint(x=5, y=0, z=3, p=5),
        og.LoadPoint(x=5, y=0, z=5, p=5),
    ]
    ref_ans = [
        og.LoadPoint(x=5, y=0, z=3, p=5),
        og.LoadPoint(x=8, y=0, z=3, p=5),
        og.LoadPoint(x=8, y=0, z=5, p=5),
        og.LoadPoint(x=5, y=0, z=5, p=5),
    ]
    actual, _ = og.sort_vertices(point_list)
    assert actual == ref_ans

def test_create_arc_equation():
    a = og.find_circle(
        x1=0,
        y1=0,
        x2=1,
        y2=1,
        x3=2,
        y3=0,)

    print(a)

    assert a[0] == [1, 0]
    assert a[1] == 1
