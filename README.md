# Machine Learning Based Intrusion Detection System for CAN Bus
This repository contains the code for a Two Stage Intrusion Detection System,
that uses both hard-coded rules along with a neural network in order to
determine if a packet sent on a CAN bus is malicious or not.

## Installation
1. Clone this repository. If Git is installed, then run  
   `git clone https://gitlab.eecs.umich.edu/linxiz/IDS-18-Fall.git`.
1. Install [Python](https://www.python.org/downloads/). You will also need pip
   installed with Python: this is done by default.
1. Run the command `pip install .`. This will install all dependencies that
   this project requires in order for you to run it.

### Development
1. In the root of the project directory, make a virtual environment with `python -m venv .venv`.
2. Activate the venv with:
   - Linux/Mac: `source .venv/bin/activate`
   - Windows: `.\.venv\Scripts\Activate.ps1`
2. Install the application to venv in development mode with `pip install --editable '.[test]'`.
3. To run tests, run the command `python -m pytest`. This will automatically
   perform all unit tests, and you can verify that all tests pass.  
   Note: using `python -m pytest` instead of `pytest` ensures it will execute
   in the context of the virtual environment.

## Usage
TBD
