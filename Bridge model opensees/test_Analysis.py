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
    return RefTruck

@pytest.fixture
def createtestbridge():
    refbridge = pickle.load(open("save.p", "rb"))
    RefTr = createvehicle()
    RefBridge = Analysis.Grillage(refbridge,RefTr)
    return RefBridge
# - - - - - - - - - - - -
def test_vehicle(createvehicle):
    truck = createvehicle
    assert truck.direction == 'X'

# test variation of input for vehicle class
#           num, strings, bool, float, zero
truckdatatype = {20,'X',True,10.5,0}

@pytest.mark.parametrize("truck",truckdatatype)
def test_input_vehicle_alwts(createvehicle,truck):
    truck = createvehicle
    assert truck.direction == 'X'
