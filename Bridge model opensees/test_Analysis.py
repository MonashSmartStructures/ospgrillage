import pytest
from Vehicle import vehicle
import pickle
import Analysis

truckdata = {20,30,40,True}
@pytest.mark.parametrize("truckdetails",truckdata)

@pytest.fixture
def createvehicle():
    axlwts = [800, 3200, 3200]
    axlspc = [7, 7]
    axlwidth = 5
    initial_position = [0, 3.0875]
    travel_length = 50
    increment = 2
    direction = "X"
    #
    # create truck
    RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)
    return RefTruck

@pytest.fixture
def createtestbridge():
    refbridge = pickle.load(open("save.p", "rb"))
    RefTr = createvehicle()
    RefBridge = Analysis.Grillage(refbridge,RefTr)

def test_vehicle(createvehicle):
    truck = createvehicle
    assert truck.direction == 'X'

