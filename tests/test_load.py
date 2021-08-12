"""

"""
import pytest
import ospgrillage as og
import sys, os

sys.path.insert(0, os.path.abspath('../'))


# test to check compound load position relative to global are correct
def test_compound_load_positions():
    #
    location = og.create_load_vertex(x=5, z=-2, p=20)  # create load point
    Single = og.create_load(type="point", name="single point", point1=location)
    # front_wheel = PointLoad(name="front wheel", localpoint1=LoadPoint(2, 0, 2, 50))
    # Line load
    barrierpoint_1 = og.create_load_vertex(x=-1, z=0, p=2)
    barrierpoint_2 = og.create_load_vertex(x=11, z=0, p=2)
    Barrier = og.LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)

    M1600 = og.create_compound_load(name="Lane and Barrier")
    M1600.add_load(load_obj=Single)
    M1600.add_load(load_obj=Barrier)  # this overwrites the current global pos of line load
    # the expected midpoint (reference point initial is 6,0,0) is now at 9,0,5 (6+3, 0+0, 5+0)
    # when setting the global coordinate, the global coordinate is added with respect to ref point (9,0,5)
    # therefore (3+4, 0+0, 3+5) = (13,0,8)
    # M1600.set_global_coord(og.Point(4, 0, 3))
    a = 2
    # check if point Single is same as point Single's load vertex
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(x=5, y=0, z=-2, p=20)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=-1, y=0, z=0, p=2)
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(x=11.0, y=0, z=0, p=2)

    # now we set global and see if correct
    M1600.set_global_coord(og.Point(4, 0, 3))
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(x=9, y=0, z=1, p=20)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=3, y=0, z=3, p=2)
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(x=15.0, y=0, z=3, p=2)