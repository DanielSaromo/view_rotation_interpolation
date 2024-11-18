## Installation
```
conda create -n viewrot python=3.12 pinocchio matplotlib
conda activate viewrot
pip install meshcat
```
If you have never used conda before, you might need to add conda-forge channel:
```
conda config --add channels conda-forge
```
## Usage
This repo is created to visually inspect rotation interpolation functions.

Replace the functions in main (see `TODO` elements).

Run the code and expect to see three new browser tabs with different cases of rotation and three interpolation functions per tab.

The interpolation functions go left to right (at y=0, y=1 and y=2), same order as in the task description.

Please include the screenshots in your report
