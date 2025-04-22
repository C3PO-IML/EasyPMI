# This file is part of EasyPMI project.
#
# Post mortem delay claculator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License 3, as published by
# the Free Software Foundation.
#
# Post mortem delay claculator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Post mortem delay claculator. If not, see <https://www.gnu.org/licenses/>.

"""
Main entry point for the EasyPMI Streamlit application.

This script configures the Python path to ensure all modules are found
and then launches the main user interface defined in the streamlitGUI package.
It serves as the single command to run the application both locally and
for deployment.

Functionality:
    1. Adjusts sys.path: Adds the project's root directory to the Python path,
       allowing absolute imports like 'from core import ...' and
       'from streamlitGUI import ...' to work correctly regardless of how
       the script is executed.
    2. Imports UI Builder: Imports the 'build_main_ui' function from
       'streamlitGUI.run' module *after* the path is configured.
    3. Executes UI: If run as the main script (__name__ == "__main__"),
       it calls 'build_main_ui()' to construct and display the Streamlit interface.

Usage:
    To run the application locally:
        streamlit run EasyPMI.py
    For deployment (e.g., Streamlit Community Cloud):
        Set 'EasyPMI.py' as the main application file.
"""

import sys
import os

# --- Path configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the main user interface function AFTER configuring the path
from streamlitGUI.run import build_main_ui

if __name__ == "__main__":
    build_main_ui()