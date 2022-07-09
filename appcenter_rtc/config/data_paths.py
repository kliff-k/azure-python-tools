import os
import platform


# Checks which OS is running the script in order to properly save/retrieve user data
if platform.system() == 'Windows':
    # Local App Data is used for Windows
    local_data_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'CEF', 'appcenter_rtc')
    local_data_file = os.path.join(local_data_folder, 'user_data.dat')
    local_hash_file = os.path.join(local_data_folder, 'data_validation.dat')
else:
    # For Linux, try user defined XDG_DATA_HOME. If not available, write to running user's $HOME/.local/share
    xdg_path = os.getenv('XDG_DATA_HOME')
    data_home_path = xdg_path if xdg_path else os.path.join(os.getenv('HOME'), '.local', 'share')
    local_data_folder = os.path.join(data_home_path, 'CEF', 'appcenter_rtc')
    local_data_file = os.path.join(local_data_folder, 'user_data.dat')
    local_hash_file = os.path.join(local_data_folder, 'data_validation.dat')
