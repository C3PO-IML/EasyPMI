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
Launches a Streamlit application from a Python script.

This script starts a Streamlit application contained in the 'streamlitGUI/run.py' file
without automatically opening a web browser (headless mode).

Details:
    - Imports the necessary modules from Streamlit
    - Configures headless mode (no automatic browser opening)
    - Executes the specified Streamlit application

Parameters for the run function:
    - 'streamlitGUI/run.py': Path to the Streamlit script to execute
    - args=[]: List of arguments to pass to the script
    - flag_options=[]: Additional configuration options
    - is_hello=False: Indicates this is not the demo application

Usage example:
    This script can be run directly to start the Streamlit application
    in a controlled environment, such as when integrating with another application
    or for automated testing.
"""

from streamlit import config as _config
from streamlit.web.bootstrap import run

_config.set_option("server.headless", True)
run('streamlitGUI/run.py', args=[], flag_options=[], is_hello=False)