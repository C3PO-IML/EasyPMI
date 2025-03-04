This repository contains a Python application for estimating short post-mortem interval (PMI) using various methods and parameters. 
The application leverages numerical methods and empirical data to provide accurate estimations of the time since death.

### Features
-**Henssge Method**: Estimates PMI using rectal or brain temperature (*We recommend measuring tymanic temperature with a probe*).  
-**Baccino Method**: Estimates PMI using tympanic temperature with a linear cooling model.  
-**Thanatological Signs**: Estimates PMI based on idiomuscular reactions, rigor mortis, lividity, and other post-mortem changes.  
-**Customizable Parameters**: Allows manual input of corrective factors, body conditions, and environmental factors.  
-**Graphical Visualization**: Provides plots for thermal decay curves and comparative PMI results.  
-**PDF Report Generation**: Generates a PDF report of the results for easy sharing and documentation.  

### Installation
To run the application locally, you need to have Python installed on your system (this apllication was developed with python 3.13.2).  

Clone the Repository:
```bash
git clone https://github.com/C3PO-IML/EasyPMI.git
```

Install the required Python packages :
```bash
pip install -r requirements.txt
```

Run Application:
```bash
streamlit run EasyPMI.py
```

### Usage 
-<ins>Enter Parameters</ins>: Use the sidebar to input the necessary parameters such as tympanic temperature, rectal temperature, ambient temperature, body weight, corrective factor, body condition, environment, supporting base, and thanatological signs.

-<ins>Calculate Results</ins>: Click the "Calculate" button to compute the PMI using the entered parameters.

-<ins>Reset Parameters</ins>: Click the "Reset" button to clear all inputs and start over.

-<ins>Download PDF Report</ins>: Click the "Download PDF" button to generate and download a PDF report of the results.

### Code Structure
The code is structured into several functions and sections:

-**Constants**: Defines temperature limits and corrective factors.  
-**Utility Functions**: Functions for converting decimal separators, formatting time, and determining corrective factors.  
-**Calculation Functions**: Functions for calculating PMI using Henssge and Baccino methods, and for estimating PMI based on thanatological signs.  
-**Plotting Functions**: Functions for generating plots of thermal decay curves and comparative PMI results.  
-**User Interface Management Functions**: Functions for managing the user interface, including resetting fields and calculating results.  
-**PDF Generation Function**: Function for generating a PDF report of the results.

### Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

### License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

### Acknowledgments
The methods and empirical data used in this application are based on the work of Henssge and Baccino, as well as other forensic science research.
Special thanks to the contributors and maintainers of the libraries used in this project.
Contact
For any questions or support, please contact clement.poulain@chu-brest.fr
