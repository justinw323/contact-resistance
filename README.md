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
     
# Usage
1. Open the application (contact_resistance.exe or contact_resistance_fast.exe)
2. Go to the Parameters page and load in parameters
   1. Manually typed in parameters are loaded in by pressing the "Load Current Parameters" button. You can also save parameters as a preset by entering a name in the "Preset name" field and hitting "Save Current Parameters".
   2. To load parameters from a preset, select a preset from the dropdown menu (which will only appear if at least one preset has been saved. With a preset selected, press "Load preset" to load the parameters into the system, or press "Delete preset" to erase the preset (this cannot be undone).
   3. If the parameters you try to load in are invalid, a message will flash telling you. Examples of invalid parameters include incomplete rows, or non-number parameters.
   4. Note: The system will load parameters in until it sees an empty row. If, for example, you have parameters for steps 1-7 written, an empty row for step 8, and parameters for step 9, only steps 1-7 will be loaded in
   5. The "Zero TPR" button fills the "GDL Through Plate Resistance" column with 0 for a calibration run. If you do not need to run 20 steps, enter your parameters then delete everything in the row after the last row of the measurement (the program will stop once it sees an empty row)
3. With parameters loaded in, return to the measurement page and you should see a message indicating that you are ready to begin a measurement. Make sure that the sample is clamped and that the current source is on (current will not flow until the measurement begins). When ready, begin the measurement by pressing "Start".
4. A label below the graph tells you what step you are on. After a step is completed, measurement information is added to the table, and the graph is updated. To stop a run, press the "Stop" button.
   1. Note: if you move the application window (or click and hold on the title bar), the entire program freezes, which will result in the current measurement taking longer than it should. Avoid moving the application window or clicking and holding on the title bar while a measurement is in progress.
5. When the measurement is complete. You can enter notes about the measurement in the corresponding text box, and save information from the measurement to an Excel sheet by entering a file name in the "File Name" box and hitting "Save to Excel".
6. You can also copy information from a particular step by hitting the corresponding "Copy Row" button to paste into Excel. You may have to change some settings in your Excel sheet to paste the information into multiple cells:
   1. First paste the measurement data into a cell.
   2. Select the data and go to the Data tab in the Excel sheet, and click "Text to Columns".
   3. Select "Delimited" and hit "Next", and on the following space check the "Space" option. Hit "Finish". The data should now be in three separate cells
7. If the previous run was a calibration run, you can return to the Parameters page and press "Copy TPR" to copy the TPR data from the last measurement into the GDL Through Plate Resistance column.

# Notes
1. To clamp the electrodes using the application, click "Pressure on" to turn on the air, then turn the lever to lower the clamp. Turn the lever back to raise the clamp again. If you click "Pressure off", the clamp will be stuck in its current position until you turn the air back on (either with the application or manually) and turn the lever.
2. The application will automatically clamp when starting a measurement, but you should clamp the sample beforehand to make sure that everything is lined up.
3. You can have multiple contact resistance applications open at a time, but only one can be connected to the LabJack. The application will open a connection to the Labjack when you hit "Start" (to start a measurement) or hit "Pressure on" (to turn the air on). The connection will close once either the measurement stops, you hit "Stop" during an active measurement, or you hit "Pressure off" after hitting "Pressure on". If there is not active measurement being performed, and the application is not sending a signal to clamp, then the application has no open connection with the Labjack, and you can use another application to connect to it (ie. to run a measurement).
