from unicodedata import name
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

    def getName(self):
        return self.name

#this class is used to create unique loader objects
class Loader:
    def __init__(self, name, bucketCap, swingTime, truckSetupTime, truckCycleTime):
        self.name = name
        self.bucketCap = bucketCap
        self.swingTime = swingTime
        self.truckSetupTime = truckSetupTime
        self.truckCycleTime = truckCycleTime

    #returns the loading time of a truck object. No fractional swings allowed
    def getLoadingTime(self, truckType):
        return (math.floor(truckType.capacity/self.bucketCap)+1)*self.swingTime+self.truckSetupTime
    
    #returns the cycle time any truck takes to go from the loader to the destination point and then back
    def getCycleTime(self):
        return self.truckCycleTime

    def getName(self):
        return self.name

#this class combines different trucktypes and loaders and calculates optimal assignments
class Fleet:
    def __init__(self):
        self.truckFleet = []
        self.loaders = []
        self.assignmentMatrix = []

    def addTrucks(self, truckType, numTrucks):
        self.truckFleet += [[truckType,numTrucks]]

    def addLoader(self, loader):
        self.loaders += [loader]

    #this function uses integer programming to solve the match factor problem
    #Also calls functions at the end to format and display output
    def optimize(self,desiredMF=1):
        [A,B,C] = self.makeSolverMatrices(desiredMF)
        print("A matrix (rounded) *********************************************************")
        print(np.round(A,3))
        print("b matrix *******************************************************************")
        print(B)
        print("c matrix *******************************************************************")
        print(C)
        print("Solver Results *************************************************************")
        numConstraints = self.numConstraints()
        numVar = self.numVar()

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

        #define constraints
        for i in range(numConstraints):
            #in the case of the delta variables, negative variables are allowed
            if (i > len(self.truckFleet)):
                constraint = lp.RowConstraint(-infinity, B[i], '')
            else:
                constraint = lp.RowConstraint(0, B[i], '')
            for j in range(numVar):
                constraint.SetCoefficient(x[j], A[i,j])

        #sets up objective function
        objective = lp.Objective()
        for j in range(numVar):
            objective.SetCoefficient(x[j], C[j])
        objective.SetMinimization()

        #solves IP problem
        status = lp.Solve()

        #Displays IP solver results. Useful for troubleshooting
        if status == pywraplp.Solver.OPTIMAL:
            print('Objective value =', lp.Objective().Value())
            for j in range(numVar):
                print(x[j].name(), ' = ', x[j].solution_value())
            print('Problem solved in %f milliseconds' % lp.wall_time())
            print('Problem solved in %d iterations' % lp.iterations())
            print('Problem solved in %d branch-and-bound nodes' % lp.nodes())
        else:
            print('The problem does not have an optimal solution.')
        
        self.parseAssignmentMatrix(x)
        self.printMatchFactors(x)
        self.printAssignmentMatrix()

    #creates an easy to interpret assignemtn matrix from the complicated variable vector
    def parseAssignmentMatrix(self,x):
        self.assignmentMatrix = np.zeros([self.numTruckTypes(),self.numLoaders()])
        i = 0
        for r in range(self.numTruckTypes()):
            for c in range(self.numLoaders()):
                self.assignmentMatrix[r,c] = x[i].solution_value()
                i = i + 1
        
    #creates the classic Ax=b, Min/Max xc matrices for a linear program
    #Consult the documentation for how the constraints and variables are formulated
    def makeSolverMatrices(self,desiredMF=1):
        numLoaders = self.numLoaders()
        numTruckTypes = self.numTruckTypes()
        numVar = self.numVar()
        numConstraints = self.numConstraints()

        A = np.zeros([numConstraints,numVar])
        B = np.zeros(numConstraints)
        C = np.zeros(numVar)

        for i in range(numTruckTypes*numLoaders,numVar):
            C[i] = 1

        #keymatrix is a helper matrix to identify which truck and loader each variable is related to
        keyMatrix = self.keyMatrix()

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
    

    def printAssignmentMatrix(self):
        print("Assignment Matrix *******************************************************")
        print(str(["RESULT"]+[l.getName() for l in self.loaders]))
        for r in range(self.numTruckTypes()):
            print([str(self.truckFleet[r][0].getName())]+list(self.assignmentMatrix[r,:]))
    
    #Displays the result of IP solver in terms of match factor
    #THis is not match factor per se, but rather the absolute value of the deviation
    #from the desired match factor inputted into the optimize() function. The default MF is 1
    def printMatchFactors(self,x):
        print("Match Factors *******************************************************")
        print(str(["MF DELTAS"]+[l.getName() for l in self.loaders]))
        #pulls out the match factors deltas from the IP solution
        #these are the absolute value of the difference of 
        mfs = []
        for i in range(self.numTruckTypes()*self.numLoaders(),self.numVar()):
            mfs += [round(x[i].solution_value(),3)]
        print(["(Desired MF +/-)"]+mfs)
                
    #helper functions to calculate commonly used values
    def numLoaders(self):
        return len(self.loaders)

    def numTruckTypes(self):
        return len(self.truckFleet)

    def numVar(self):
        return self.numLoaders()+self.numLoaders()*self.numTruckTypes()

    def numConstraints(self):
        return self.numTruckTypes()+2*self.numLoaders()

    #keymatrix is a helper matrix to identify which truck and loader each variable is related to.
    #since variables refer to a truck-loader pair, when the variables are listed in 1D order,
    #it can be difficult to know which truck-loader pair a variable is for. This is an index for that.
    def keyMatrix(self):
        keyMatrix = np.zeros([self.numVar(), 2])
        i = 0
        for t in range(self.numTruckTypes()):
            for l in range(self.numLoaders()):
                keyMatrix[i,0] = t
                keyMatrix[i,1] = l
                i = i + 1
        #negative numbers are used to indicate the variable is a delta variable and not associated with truck or loader
        for i in range(self.numTruckTypes()*self.numLoaders(),self.numVar()):
            keyMatrix[i,0] = -1
            keyMatrix[i,1] = -1
        return keyMatrix

