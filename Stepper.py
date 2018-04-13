import Slush

class Stepper(Slush.Motor):
    b = Slush.sBoard()
    
    #Stepper constructor, if no setCurrent params are given defaults to 20
    def __init__(self, **kwargs):
        super().__init__(kwargs.get("port", 0))
        self.resetDev()
        self.microSteps = kwargs.get("microSteps", 0)
        self.setMicroSteps(self.microSteps)
        self.setCurrent(kwargs.get("runCurrent", 20), kwargs.get("accelCurrent", 20), kwargs.get("deaccelCurrent", 20), kwargs.get("holdCurrent", 20))

    def getMicroSteps(self):
        return self.microSteps
