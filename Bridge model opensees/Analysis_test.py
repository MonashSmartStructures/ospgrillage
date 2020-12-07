import unittest
from Bridgemodel import *  # bridge opensees model
from Bridge_member import BridgeMember  # bridge opensees model
from Vehicle import *
import Analysis
import pickle


class TestBridgeOPpy(unittest.TestCase):
    def test_vehicle(self):
        # Assume
        axlwts = [800, 3200, 3200]
        axlspc = [7, 7]
        axlwidth = 5
        initial_position = [0, 3.0875]
        travel_length = 50
        increment = 2
        direction = "X"

        # Action
        RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)

        # Assert
        self.assertTrue(RefTruck)


if __name__ == '__main__':
    unittest.main()
