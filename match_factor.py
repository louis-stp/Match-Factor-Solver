from ortools.linear_solver import pywraplp
import numpy as np

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
        lp = pywraplp.Solver.CreateSolver('SCIP')
        infinity = lp.infinity()
        numLoaders = len(self.loaders)
        numTruckTypes = len(self.truckFleet)

        A = makeA()
        
        #adds the assignment variables to the integer problem
        #These define how many of truck type i is assigned to loader j
        x = []
        for i in range(numTruckTypes):
            for j in range(numLoaders):
                x += [lp.IntVar(0, infinity, 'x_'+str(i)+'_'+str(j))]

        #Adds the delta variables. These variables measure the absolute value of
        #the match factor of each loader from the desired match factor (default 1).
        d = []
        for j in range(numLoaders):
            d += [lp.IntVar(0,infinity, 'd_'+str(j))]

        #constrains the total number of each type of truck 
        for i,truck in enumerate(self.truckFleet):
            maxTrucks = list(truck.values())[0]
            constraint = lp.RowConstraint(0, maxTrucks, '')
            #sums the number of trucks over all loaders. Hence coeff = 1 for relevant coeffs and 0 otherwise
            for k in range(len(x)):
                

        #sets the delta constraints
        for l in range(len(d)):
            constraint = lp.RowConstraint(0, 1, '')

    def makeA(self):
        numLoaders = len(self.loaders)
        numTruckTypes = len(self.truckFleet)
        numVar = numLoaders+numLoaders*numTruckTypes
        A = np.zeros([numVar,numVar])

        for i in range(numTruckTypes):
            for k in range(numVar):
                if(k >= i*numTruckTypes)
                A[]
        
        #make truck model number constraint rows
        


                

            

fleet = Fleet()
fleet.addTrucks(TruckType("CAT797",400), 5)
fleet.addTrucks(TruckType("CAT777",100), 4)
fleet.addLoader(Loader("Bucyrus_1",55,.25,1,2000))
fleet.addLoader(Loader("Bucyrus_2",55,.25,1,1500))
fleet.optimize()

    