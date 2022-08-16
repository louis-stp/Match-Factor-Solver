# Match Factor Solver

A python module for computing the optimal assignment of trucks to loaders in a heterogeneus fleet. It optimizes the parameter referred to as Match Factor (MF), which reduces lost production potential for both trucks and loaders.

## Table of Contents

- [Installation](#installation)
- [Technical_Review](#Technical_Review)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

## Installation

Download the dependencies if necessary and then clone this repo. Dependencies: numpy, ortools

```sh
pip install numpy
python -m pip install --upgrade --user ortools
git clone https://github.com/louis-stp/Match-Factor-Solver.git
```

## Technical_Review

### Match Factor
Match factor roughly represents the productivity of the trucks divided by the productivity of the loader. Since the productivity of the system is the minimum of these two productivities, it is ideal to have them be as close as possible to avoid wasted production potential. This translates to an MF of 1, but in reality, a higher MF may be desired since the cost of lost loader time is higher than than lost truck time.

### Base Assumptions
This model assumes a case where trucks are assigned only to one loader, and no loader grouping is allowed. Loaders also have a single destination and a single cycle time and truck setup time, regardless of truck type. Truck setup time refers to the turning and maneuvering time required to get a truck into loading position, and time it takes for a truck to get out of the way once loaded.

Truck loading time does vary by truck. This is calculated by taking the capacity of the truck divided by the capacity of the loader bucket, rounding up to the nearest integer, and multiplying that by the loader swing time, and then finally adding the truck setup time on top of that value. This value represents the numerator in the Match Factor calculation. The truck cycle time, which is constant for all trucks of the same loader, is the denominator for the MF calculation.

### Integer Programming
This module uses an Integer Program (IP) to solve for match factors for a system with multiple loaders and multiple trucks, all with potentially different properties. The objective for this IP is to minimize the deviation of the realized match factors from the desired match factors (default 1). 

#### Constraints
Since the objective is an absolute value, the program needs to be constructed in such a way to eliminate this absolute value from the objective function. It does this using two constraints to capture the difference. For example, if you want to minimize the absolute value the expression x-1, you create 2 constraints and formulate the objective function as follows:

Minimize d:<br>
x - 1 <= d <br>
1 - x <= d <br>

In this program, d is a variable, so it appears in the A matrix (Refer to Linear Programming for Ax <= b formulation for linear programs). Thus the constraints are modified to be:

Minimize d:<br>
x - d <= 1 <br>
-x - d <= -1 <br>

The above constraints are referred to as *Delta Constraints* in the code, and there are 2 per loader. There are also *Truck Constraints*, which simply limit the total number of trucks in the system to be below the provided maximums. There is 1 Truck Constraint per Truck Type.

#### Variables
There are two types of variables, *assignment variables* and *delta variables*. Assignment variables are non-negative integers which represent the number of trucks of type i assigned to loader j. There are IxJ assignment variables. There are also delta variables, each corresponding to a pair of delta constraints, as discusses in the Constraints section. The solution provides the optimal assignments for truck-loader pairs for the assignment variable, and the absolute value of the difference in Match Factor for each loader as represented for each delta variable.

#### Objective
The objective is to minimize the sum of the delta variables. Assignment variables do not appear in the objective function. No loader is weighted higher than another, although this could be possible in the future by modifying the weights in the vector c.

## Usage

### Classes
There are 3 classes in this project. TruckType, Loader, and Fleet. Fleet is the class where TruckTypes and Loaders are added to be optimized. A TruckType is a unique class of truck with unique properties. CAT 797 is a class of truck, and it could have a capacity of 400 tons in an example. A Loader is any distinct Loader in your network. Even if it is of the same model and type, it is added distinctly in the network.

### Example

```sh
#EXAMPLE CASE
fleet = Fleet()
fleet.addTrucks(TruckType(name="CAT797",capacity=430.4), numTrucks = 10)
fleet.addTrucks(TruckType(name="CAT777",capacity=117.3), numTrucks = 5)
fleet.addTrucks(TruckType(name="CAT787",capacity=233.3), numTrucks = 4)
fleet.addLoader(Loader(name="Shovel_1",bucketCap=55,swingTime=30,truckSetupTime=60,truckCycleTime=2000))
fleet.addLoader(Loader(name="Shovel_2",bucketCap=55,swingTime=30,truckSetupTime=60,truckCycleTime=1580))
fleet.optimize(1.1)
```


#### TruckType
TruckType requires the following parameters: (name, capacity)

#### Loader
Loaders requires the following parameters: (name, bucketCap, swingTime, truckSetupTime, truckCycleTime)

#### Fleet
Fleet requires no properties. TruckTypes and Loaders are added afterwards.

### Methods

#### Fleet.addTrucks(TruckType truck, int maxOfTruckType)
This is how you add a truckType to the network, and define the maximum number allowed for the given problem

#### Fleet.addLoader(Loader loader)
Add a loader object to the fleet using this method.

#### Fleet.optimize(desiredMF = 1 (defualt))
Run the optimization function using this method. You can choose a desired match factor other than 1 by passing it into the function as a parameter.
This method will print out the desired results


## Support

Please open an issue for support.

## Contributing

Please contribute using Github Flow. Create a branch, add commits, and open a pull request.
