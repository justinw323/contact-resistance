# contact-resistance
System that automatically measures contact resistance of plate sample.

# Installation
Install anaconda and set up a vitual environment following these instructions: https://www.geeksforgeeks.org/set-up-virtual-environment-for-python-using-anaconda/# (Optional)

1. Click the green "Code" button, click "Download ZIP"
2. Unzip the files and move to your choice of location
3. Ensure that the computer has LabJack software installed
   1. Installer can be found at https://labjack.com/support/software/installers
   2. Follow the onscreen instructions to install LabJack software

From a terminal:
1. Navigate to the folder containing the .spec file (label_maker.spec or label_maker_fast.spec)
2. Install the pyinstaller package with:
   1. `pip install pyinstaller`
   2. `pip3 install pyinstaller`
   3. `conda install pyinstaller` if using the Anaconda prompt
4. Run:
   1. `pyinstaller contact_resistance.spec` for the slower app. This creates two folders: build and dist. dist will contain a the file "contact_resistance.exe", which is the application.
   2. `pyinstaller contact_resistance_fast.spec` for the faster app. This creates two folders: build and dist.
        1. dist will contain another folder called "contact_resistance_fast", which will contain the "contact_resistance_fast.exe" file, as well as other files. The .exe file must be kept in that folder for the program to work, and the other files must not be deleted 
