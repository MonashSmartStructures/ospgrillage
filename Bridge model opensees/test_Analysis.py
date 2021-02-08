import pytest
from Vehicle import vehicle
import pickle
import Analysis

# - - - - - - - - - - - -
@pytest.fixture(scope='module')
def createvehicle():
    axlwts = [800, 3200, 3200]
    axlspc = [7, 7]
    axlwidth = 5
    initial_position = [0, 3.0875]
    travel_length = 50
    increment = 2
    direction = "X"
    #
    print("-----------setup truck-----------")
    # create truck
    RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)
    yield RefTruck
    print("----------test on truck finish---")

@pytest.fixture
def createtestbridge():
    refbridge = pickle.load(open("save.p", "rb"))
    RefTr = createvehicle()
    RefBridge = Analysis.Grillage(refbridge,RefTr)
    print("-------------setup grillage -------------")
    return RefBridge
# - - - - - - - - - - - -
# Tests for vehicle class
def test_vehicle(createvehicle):
    assert isinstance(createvehicle.direction,str)


# test variation of input for vehicle class
#           num, strings, bool, float, zero
truckdatatype = {int,str,bool,float}

#@pytest.mark.parametrize('truck',truckdatatype)
#def test_input_vehicle_alwts(createvehicle,truck):
    #truckd = createvehicle
    #assert isinstance(createvehicle.direction,truckdatatype)
