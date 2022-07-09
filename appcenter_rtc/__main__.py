# Import custom lib
from appcenter_rtc.lib.cli.cli import Cli
from appcenter_rtc.lib.tool.utils import Utils
from appcenter_rtc.lib.gui.gui import start_gui
import requests

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'ALL:@SECLEVEL=1'

# Entrypoint
if __name__ == '__main__':

    # Fetches script configuration
    utils = Utils()

    if utils.get_operation_mode() == 'gui':
        start_gui()
        exit(0)

    if utils.get_operation_mode() == 'cli':
        cli = Cli()
        cli.exec(utils)
        exit(0)

