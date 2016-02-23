"""
Importing certain classes into the global namespace.
"""

from beekeeper.api import API
from beekeeper.hive import Hive
from beekeeper.data_handlers import add_data_handler
from beekeeper.variable_handlers import add_variable_handler, set_content_type
from beekeeper.variable_handlers import render as render_variables