# TIGER_scripts
Test scripts for the CGEM project.

## Installation
If you have conda installed in your system, disable the conda environment before installing.\
The suggested Python version is 3.8. If it's not present in your system, install it with (on Ubuntu):
```
sudo apt install python3.8 
```
I suggest you to use a virtual environment, to do so you need python3.8-venv
```
sudo apt install python3.8-venv
```
You will also need the libpython3.8-dev package
```
sudo apt install libpython3.8-dev
```
Finally, the GUI uses tlc-tk, so install the python3 support for it:
```
sudo apt install python3-tk
```

To install GUFI run
```
python3.8 installer.py
```
And answer "yes" to create you virtual environment\
Now simply run GUFI.sh to open GUFI:
```
./GUFI.sh
```