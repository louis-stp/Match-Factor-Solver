import numpy as np
from scipy.optimize import linprog

#this class defines a type of truck which have a certain name and capacity
class TruckType:
    def __init__(self,name,capacity):
        self.capacity = capacity
        self.name = name

#this class is used to create unique loader objects
class Loader:
    def __init__(self, name, bucketCap, swingTime, truckSetupTime, truckCycleTime):
        self.bucketCap = bucketCap
        self.swingTime = swingTime
        self.truckSetupTime = truckSetupTime
        self.truckCycleTime = truckCycleTime

    #returns the loading time of a truck object. No fractional swings allowed
    def loaderCycleTime(self, truckType):
        return (truckType.capacity%self.bucketCap+1)*self.swingTime+self.truckSetupTime

#this class combines different trucktypes and loaders and calculates optimal assignments
class Fleet:
    def __init__(self):
        self.truckFleet = []
        self.loaders = []
        self.assignments = []

    def addTrucks(self, truckType, numTrucks):
        self.truckFleet += [{truckType:numTrucks}]

    def addLoader(self, loader):
        self.loaders += [loader]

    def optimize(self):
        pass

    