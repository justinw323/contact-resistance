# contact-resistance
System that automatically measures contact resistance of plate sample.

# Installation
Install anaconda and set up a vitual environment following these instructions: https://www.geeksforgeeks.org/set-up-virtual-environment-for-python-using-anaconda/# (Optional)

1. Click the green "Code" button, click "Download ZIP"
2. Unzip the files and move to your choice of location

From a terminal:
1. Navigate to the folder containing the .spec file (label_maker.spec or label_maker_fast.spec)
2. Install the pyinstaller package with:
   1. `pip install pyinstaller`
   2. `pip3 install pyinstaller`
   3. `conda install pyinstaller` if using the Anaconda prompt
4. Run:
   1. `pyinstaller contact_resistance.spec` for the slower app
   2. `pyinstaller contact_resistance_fast.spec` for the faster app
        1. This creates a folder called "contact_resistance_fast" containing the file contact_resistance_fast.exe file, as well as other files. The .exe file must be kept in that folder for the program to work, and the other files must not be deleted 
