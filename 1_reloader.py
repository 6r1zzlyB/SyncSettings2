import sys
from importlib import reload

mod_prefix = 'sync_settings'

# ST3/4 loads packages as modules, so we need the prefix (assuming directory name SyncSettings)
# If the directory is SyncSettings, this is 'SyncSettings.sync_settings'
# We try to detect the package name from __package__ if possible, but safe default is SyncSettings
# for existing users.
# However, since this file is executed dynamically, __package__ might not be reliable.
# We'll stick to the existing logic but simplified.

st_package_name = 'SyncSettings' 
# If the user renamed the folder to "SyncSettings 2", this might need adjustment,
# but usually users keep the repo name.

mod_prefix = f'{st_package_name}.{mod_prefix}'

reload_mods = []
for mod in sys.modules:
    if mod.startswith(('sync_settings', st_package_name)) and sys.modules[mod] is not None:
        reload_mods.append(mod)

mods_load_order = [
    '',

    '.libs',
    '.libs.logger',
    '.libs.path',
    '.libs.settings',
    '.libs.gist',

    '.thread_progress',
    '.sync_version',
    '.sync_manager',

    '.commands',
    '.commands.decorators',
    '.commands.open_logs',
    '.commands.download',
    '.commands.upload',
    '.commands.create_and_upload',
    '.commands.delete_and_create',
]

for suffix in mods_load_order:
    mod = mod_prefix + suffix
    if mod in reload_mods:
        try:
            reload(sys.modules[mod])
        except ImportError:
            pass
        except Exception:
            pass
