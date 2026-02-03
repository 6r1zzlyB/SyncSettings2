# -*- coding: utf-8 -*-

import importlib
import sys
import os

f = os.path.join(os.path.expanduser('~'), '.sync_settings')
if not os.path.isdir(f):
    os.mkdir(f)

# ST4 / Python 3.8+ style imports
from .sync_settings.commands import *  # noqa: F403, F401

reloader = 'SyncSettings.sync_settings.reloader'

# Make sure all dependencies are reloaded on upgrade
if reloader in sys.modules:
    importlib.reload(sys.modules[reloader])
