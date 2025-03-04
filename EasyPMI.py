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

from streamlit import config as _config
from streamlit.web.bootstrap import run

_config.set_option("server.headless", True)
run('streamlitGUI/run.py', args=[], flag_options=[], is_hello=False)