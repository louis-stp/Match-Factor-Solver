# Match Factor Solver

A python module for computing the optimal assignment of trucks to loaders in a heterogeneus fleet. It optimizes the parameter referred to as Match Factor (MF), which roughly represents the productivity trucks divided by the productivity of the loader. 

## Table of Contents

- [Installation](#installation)
- [Technical Review](#Technical Review)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

## Installation

Download the file from this repository called "match_factor.py" and use in your own project.
Dependencies: numpy, ortools

```sh
pip install numpy
python -m pip install --upgrade --user ortools
git clone 
```

## Technical Review

###Match Factor
Match factor roughly represents the productivity of the trucks divided by the productivity of the loader. Since the productivity of the system is the minimum of these two productivities, it is ideal to have them be as close as possible to avoid wasted production potential. This translates to an MF of 1, but in reality, a higher MF may be desired since the cost of lost loader time is higher than than lost truck time.

## Usage

Replace the contents of `README.md` with your project's:

- Name
- Description
- Installation instructions
- Usage instructions
- Support instructions
- Contributing instructions
- Licence

Feel free to remove any sections that aren't applicable to your project.

## Support

Please [open an issue](https://github.com/fraction/readme-boilerplate/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/fraction/readme-boilerplate/compare/).
