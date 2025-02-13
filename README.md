This repository contains a Python application for estimating the post-mortem interval (PMI) using various methods and parameters. 
The application leverages numerical methods and empirical data to provide accurate estimations of the time since death.

Features
Henssge Method: Estimates PMI using rectal or brain (tympanic) temperature.
Baccino Method: Estimates PMI using tympanic temperature with a linear cooling model.
Thanatological Signs: Estimates PMI based on idiomuscular reactions, rigor mortis, lividity, and other post-mortem changes.
Customizable Parameters: Allows manual input of corrective factors, body conditions, and environmental factors.
Graphical Visualization: Provides plots for thermal decay curves and comparative PMI results.
PDF Report Generation: Generates a PDF report of the results for easy sharing and documentation.

Installation
To run the application, you need to have Python installed on your system. Additionally, you need to install the required Python packages. You can install them using pip:

pip install numpy scipy streamlit matplotlib reportlab

Usage
Clone the Repository:
git clone https://github.com/yourusername/post-mortem-interval-calculator.git
cd post-mortem-interval-calculator

Run the Application:
streamlit run EasyPMI.py

Enter Parameters: Use the sidebar to input the necessary parameters such as tympanic temperature, rectal temperature, ambient temperature, body weight, corrective factor, body condition, environment, and thanatological signs.

Calculate Results: Click the "Calculate" button to compute the PMI using the entered parameters.

Reset Parameters: Click the "Reset" button to clear all inputs and start over.

Download PDF Report: Click the "Download PDF" button to generate and download a PDF report of the results.

Code Structure
The code is structured into several functions and sections:

Constants: Defines temperature limits and corrective factors.
Utility Functions: Functions for converting decimal separators, formatting time, and determining corrective factors.
Calculation Functions: Functions for calculating PMI using Henssge and Baccino methods, and for estimating PMI based on thanatological signs.
Plotting Functions: Functions for generating plots of thermal decay curves and comparative PMI results.
User Interface Management Functions: Functions for managing the user interface, including resetting fields and calculating results.
PDF Generation Function: Function for generating a PDF report of the results.

Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

Acknowledgments
The methods and empirical data used in this application are based on the work of Henssge and Baccino, as well as other forensic science research.
Special thanks to the contributors and maintainers of the libraries used in this project.
Contact
For any questions or support, please contact clement.poulain@chu-brest.fr
