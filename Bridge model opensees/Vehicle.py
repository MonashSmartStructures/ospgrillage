class vehicle:
    def __init__(self,axles_weight,axles_spacing,width,initial_position,travel_length, increment,direction): # UNIT: Newton (N) and meter (m)
        """Init class: use units Newton(N) and metre (m)"""
        # truck properties
        self.axles_weight = axles_weight
        self.axles_spacing = axles_spacing
        self.width = width
        self.L_truck = sum(axles_spacing)
        # test of vehicle data
        self.check_data()

        # movement properties
        self.initial_position = initial_position # array [1x2]
        self.travel_length = travel_length # float
        self.increment = increment # float
        self.direction = direction # string

    def check_data(self):
    # Input type
        if type(self.axles_weight) != list or type(self.axles_spacing) != list:
            print('Axles weight and axles_spacing input need to be list')
        if type(self.width) != int:
            print('Truck width need to be a number')
    # Positive input check:
            self.cond_W = all(ele > 0 for ele in self.axles_weight)
            cond_S = all(ele > 0 for ele in self.axles_spacing)
        try:
            if str(self.cond_W) == 'False' or self.width <=0 :
                print('Truck definitions should be positive and greater than 0')
        except:
            pass





