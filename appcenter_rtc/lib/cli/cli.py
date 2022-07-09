from typing import ClassVar
from appcenter_rtc.lib.api.jazz_rtc import JazzRtc
from appcenter_rtc.lib.api.app_center import AppCenter


class Cli:
    """
    Cli operation mode class
    """
    def exec(self, utils: ClassVar):
        """
        Executes the script in CLI mode based on pre-build configuration file
        :param utils: Configuration Class Object
        :return: None
        """

        config = utils.get_config()

        if config['report']:
            rtc = JazzRtc(config['user'], config['pass'])

        else:
            # Instantiates required lib
            rtc = JazzRtc(config['user'], config['pass'])
            ac = AppCenter(config['ac_api_key'])

            # Fetches error group list
            groups_list = []
            for version in config['version']:
                response = ac.get_error_group_list(config['app'], version, config['top'])
                if 'errorGroups' not in response:
                    continue

                group_info = {
                    'version': version,
                    'app_name': config['app'],
                    'groups': response['errorGroups']
                }
                groups_list.append(group_info)

            # Main loop
            for groups_info in groups_list:
                for group in groups_info['groups']:

                    # Error Groups with annotations or closed states are ignored
                    if 'annotation' in group or group['state'] == "Closed":
                        continue

                    # Fetches the exception stack for the current error group
                    frames = ac.exception(groups_info['app_name'], group['errorGroupId'])['exception']['frames']

                    # Prepares OSLC payload
                    post_body = utils.prepare_rtc_payload(group, frames, groups_info)

                    # POSTs the work item payload and captures the returned ID for AppCenter error group annotation
                    wi_id = rtc.post(post_body)['dc:identifier']

                    # Prepares Error Group annotation
                    wi_annotation = f"Item de Backlog: {rtc.url(config['rtc_community'], wi_id)}"

                    # Adds annotation with Work Item URL back to the Error Group
                    ac.patch(groups_info['app'], group['errorGroupId'], wi_annotation)

                    # Prints created Work Item URL
                    print(wi_annotation)
