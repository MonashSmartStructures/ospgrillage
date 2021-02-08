class vehicle:
    def __init__(self,axles_weight,axles_spacing,width,initial_position,travel_length, increment,direction): # UNIT: Newton (N) and meter (m)
        """Init class: use units Newton(N) and metre (m)"""
        # truck properties
        self.axles_weight = axles_weight
        self.axles_spacing = axles_spacing
        self.width = width
        self.L_truck = sum(axles_spacing)


        # movement properties
        self.initial_position = initial_position # array [1x2]
        self.travel_length = travel_length # float
        self.increment = increment # float
        self.direction = direction # string

        # test of vehicle data
        self.check_data()

    def check_data(self):
        """
        Function to verify inputs of class
        :return:
        """
    # Input type
        if type(self.axles_weight) != list or type(self.axles_spacing) != list:
            raise TypeError('Axles weight and axles_spacing input need to be list')
        if not isinstance(self.width,(int,float)):
            raise TypeError('Truck width need to be a number')
        if not isinstance(self.increment,(int,float)):
            raise TypeError('Increment defined as a list - increment needs to be a float or int')
        if not isinstance(self.travel_length,(int,float)):
            raise TypeError('travel length defined as a list - increment needs to be a float or int')
        if not isinstance(self.initial_position,(list)):
            raise TypeError('Initial position needs to be list of coordinate [x,y,z] - default y = 0')
        # check direction - set direction if TypeError
        if not isinstance(self.direction,str):
            print("Truck direction needs to be a string [X Y or Z]")
            # set to default X direction
            self.direction = "X"
            print("setting direction to default X ")

    # Check for non-negative value:
        check_negative(self.axles_weight)
        check_negative(self.axles_spacing)
        check_negative(self.width)
        check_negative(self.initial_position)
        check_negative(self.travel_length)
        check_negative(self.increment)

def check_negative(variable):
    """
    function to check if attributes(int,list,float) are negative
    :param variable: Attribute of class
    :return: Raise Value error if negative detected
    """
    if any(attri<0 for attri in variable):
        raise ValueError("Values in :{} are negative".format(variable))
