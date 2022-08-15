from ortools.linear_solver import pywraplp
import numpy as np
import math

#this class defines a type of truck which have a certain name and capacity
class TruckType:
    def __init__(self,name,capacity):
        self.capacity = capacity
        self.name = name

    def getCapacity(self):
        return self.capacity

#this class is used to create unique loader objects
class Loader:
    def __init__(self, name, bucketCap, swingTime, truckSetupTime, truckCycleTime):
        self.bucketCap = bucketCap
        self.swingTime = swingTime
        self.truckSetupTime = truckSetupTime
        self.truckCycleTime = truckCycleTime

    #returns the loading time of a truck object. No fractional swings allowed
    def getLoadingTime(self, truckType):
        return (math.floor(truckType.capacity/self.bucketCap)+1)*self.swingTime+self.truckSetupTime
    
    def getCycleTime(self):
        return self.truckCycleTime


#this class combines different trucktypes and loaders and calculates optimal assignments
class Fleet:
    def __init__(self):
        self.truckFleet = []
        self.loaders = []
        self.assignments = []

    def addTrucks(self, truckType, numTrucks):
        self.truckFleet += [[truckType,numTrucks]]

    def addLoader(self, loader):
        self.loaders += [loader]

    def optimize(self):
        [A,B,C] = self.makeMatrices()
        print(A)
        print(B)
        print(C)
        [numConstraints, numVar] = A.shape

        lp = pywraplp.Solver.CreateSolver('SCIP')
        infinity = lp.infinity()

        #creates variables
        #assignement variables are integers, delta variables are numerical
        x = {}
        for j in range(numVar):
            if (j < len(self.truckFleet)*len(self.loaders)):
                x[j] = lp.IntVar(0, infinity, 'x[%i]' % j)
            else:
                x[j] = lp.NumVar(0, infinity, 'x[%i]' % j)
        print('Number of variables =', lp.NumVariables())

        #define constraints
        for i in range(numConstraints):
            #in the case of the delta variables, negative variables are allowed
            if (i > len(self.truckFleet)):
                constraint = lp.RowConstraint(-infinity, B[i], '')
            else:
                constraint = lp.RowConstraint(0, B[i], '')
            for j in range(numVar):
                constraint.SetCoefficient(x[j], A[i,j])
        print('Number of constraints =', lp.NumConstraints())

        #sets up objective function
        objective = lp.Objective()
        for j in range(numVar):
            objective.SetCoefficient(x[j], C[j])
        objective.SetMinimization()

        #solves IP problem
        status = lp.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            print('Objective value =', lp.Objective().Value())
            for j in range(numVar):
                print(x[j].name(), ' = ', x[j].solution_value())
            print()
            print('Problem solved in %f milliseconds' % lp.wall_time())
            print('Problem solved in %d iterations' % lp.iterations())
            print('Problem solved in %d branch-and-bound nodes' % lp.nodes())
        else:
            print('The problem does not have an optimal solution.')

        
    def makeMatrices(self):
        numLoaders = len(self.loaders)
        numTruckTypes = len(self.truckFleet)
        numVar = numLoaders+numLoaders*numTruckTypes
        numConstraints = numTruckTypes+2*numLoaders

        desiredMF = 1
        A = np.zeros([numConstraints,numVar])
        B = np.zeros(numConstraints)
        C = np.zeros(numVar)

        for i in range(numTruckTypes*numLoaders,numVar):
            C[i] = 1

        #keymatrix is a helper matrix to identify which truck and loader each variable is related to
        keyMatrix = np.zeros([numVar, 2])
        i = 0
        for t in range(numTruckTypes):
            for l in range(numLoaders):
                keyMatrix[i,0] = t
                keyMatrix[i,1] = l
                i = i + 1
        #negative numbers are used to indicate the variable is a delta variable and not associated with truck or loader
        for i in range(numTruckTypes*numLoaders,numVar):
            keyMatrix[i,0] = -1
            keyMatrix[i,1] = -1

        #adds the sum(trucks) <= maxTrucks constraints for each truck type
        for t in range(numTruckTypes):
            for c in range(numVar):
                if(keyMatrix[c,0] == t):
                    A[t,c] = 1
            B[t] = self.truckFleet[t][1]

        #Adds the X - delta <= MF constraints
        for i in range(numTruckTypes, numTruckTypes+numLoaders):
            l = i - numTruckTypes
            for c in range(numVar):
                if (keyMatrix[c,1]==l):
                    t = int(keyMatrix[c,0])
                    loadingTime = self.loaders[l].getLoadingTime(self.truckFleet[t][0])
                    cycleTime = self.loaders[l].getCycleTime()
                    A[i,c] = loadingTime/cycleTime ##remember to change, this is just a test TODO
                if (c-l == numTruckTypes*numLoaders):
                    A[i,c] = -1
                B[i] = desiredMF
        
        #Adds the -X - delta <= -MF constraints
        for i in range(numTruckTypes+numLoaders, numTruckTypes+numLoaders*2):
            l = i - (numTruckTypes+numLoaders)
            for c in range(numVar):
                if (keyMatrix[c,1]==l):
                    t = int(keyMatrix[c,0])
                    loadingTime = self.loaders[l].getLoadingTime(self.truckFleet[t][0])
                    cycleTime = self.loaders[l].getCycleTime()
                    A[i,c] = -1*loadingTime/cycleTime ##remember to change, this is just a test TODO
                if (c-l == numTruckTypes*numLoaders):
                    A[i,c] = -1
                B[i] = -1*desiredMF

        return [A,B,C]

        
        #make truck model number constraint rows

fleet = Fleet()
fleet.addTrucks(TruckType("CAT797",400), 5000)
fleet.addTrucks(TruckType("CAT777",100), 4000)
fleet.addTrucks(TruckType("CAT787",200), 3000)
fleet.addLoader(Loader("Bucyrus_1",55,30,60,2000))
fleet.addLoader(Loader("Bucyrus_2",55,30,60,1500))
fleet.optimize()

    