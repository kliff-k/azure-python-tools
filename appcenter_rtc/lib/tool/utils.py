import json
import getpass
import datetime
import argparse
import urllib3


class Utils:
    """
    Main application configuration and setup core utility class
    """

    def __init__(self, config_file_path: str = "./config.json"):
        """
        Sets up configuration variables and script arguments/options
        :param config_file_path: Script configuration file path. Needed for CLI operation mode.
        """

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Initialize argument parser
        description = "Internal SICTM utility to export AppCenter error groups into Jazz RTC work items"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-i", "--cli", action='store_true', help="CLI operation mode")
        parser.add_argument("-r", "--report", action='store_true', help="Generate weekly changes report")
        parser.add_argument("-c", "--config", help="Script configuration file path")
        args = parser.parse_args()

        # Initializes configuration variable
        self.__config = {}

        # Sets config file path
        self.__config_file_path = config_file_path

        # Sets GUI as the default operation mode
        self.__config['operation_mode'] = "gui"

        # Overrides default config file path if --config is provided
        if args.config:
            self.__config_file_path = args.config

        if args.report:
            self.__config['report'] = True

        # Sets up CLI operation mode
        if args.cli or args.report:
            self.__cli_mode()

    def get_config(self) -> dict:
        """
        Get script configuration variables
        :return: Variable dictionary
        """
        return self.__config

    def get_operation_mode(self) -> str:
        """
        Get app operation mode
        :return: Operation mode string
        """
        return self.__config['operation_mode']

    def prepare_rtc_payload(self, group: dict, frames: dict, group_info: dict) -> str:
        """
        Prepare OSLC payload to be sent to API
        :param group: Error group dictionary as returned by AppCenter GET endpoints
        :param frames: Error group exception Stack dictionary as returned by AppCenter GET endpoints
        :param group_info: Error group origin App information (app_name, version, os)
        :return:
        """

        # Fetches request body templates
        post_body = self.__get_payload_template()
        post_description = self.__get_description_template()

        # Coalesces the first few frames in the stack for use in the work item description
        stack_trace = ""
        for frame in frames[1:7]:
            stack_trace += frame['code_raw'] + "<br/>"

        # Populates the OSLC description
        post_description = (post_description
                            .replace("{{app_name}}", group_info['app_name'])
                            .replace("{{count}}", f"{group['count']}")
                            .replace("{{date}}", self.__config['date'])
                            .replace("{{error_group_id}}", group['errorGroupId'])
                            .replace("{{code_raw}}", group['codeRaw'])
                            .replace("{{exception}}", f"{group['exceptionType']}:{group['exceptionMessage']}")
                            .replace("{{stack_trace}}", stack_trace)
                            .replace("{{version}}", group_info['version'])
                            .replace("{{os}}", group_info['os'].upper())
                            )

        # Populates the OSLC template with the AppCenter error group info
        post_body = (post_body
                     .replace("{{title}}", f"{group['codeRaw']} - Versão {group_info['version']} - {group_info['os'].upper()} - AppCenter")
                     .replace("{{description}}", post_description)
                     .replace("{{context_id}}", self.__config['rtc_context_id'])
                     .replace("{{user}}", self.__config['user'])
                     .replace("{{owner}}", self.__config['rtc_owner'])
                     .replace("{{iteration_id}}", self.__config['rtc_iteration_id'])
                     .replace("{{team_id}}", self.__config['rtc_team_id'])
                     )

        return post_body

    def __get_payload_template(self, template_file: str = "./templates/post_work_item_template.json") -> str:
        """
        Fetches payload json template
        :param template_file: Work Item json template file path
        :return: Template string
        """
        with open(template_file, 'r') as json_file:
            template = json_file.read()

        return template

    def __get_description_template(self, template_file: str = "./templates/description_work_item_template.html") -> str:
        """
        Fetches payload description template
        :param template_file: Work Item description html template file path
        :return: Template string
        """
        with open(template_file, 'r', encoding='utf8') as html_file:
            template = html_file.read()

        return template

    def __cli_mode(self) -> None:
        """
        Sets up CLI mode variables
        :return: None
        """
        with open(self.__config_file_path, 'r') as json_file:
            self.__config = json.load(json_file)

        # Sets operation mode
        self.__config['operation_mode'] = "cli"

        # Sets current date
        self.__config['date'] = datetime.datetime.now().strftime('%d/%m/%Y')

        # Fetches user credentials and/or AppCenter API key if they are not present in the configuration file
        # Username
        if 'user' not in self.__config or not self.__config['pass']:
            self.__config['user'] = input("User: ")

        # Password
        if 'pass' not in self.__config or not self.__config['pass']:
            self.__config['pass'] = getpass.getpass("Password: ")

        # AppCenter API Key
        if not self.__config['report']:
            if 'ac_api_key' not in self.__config or not self.__config['ac_api_key']:
                self.__config['ac_api_key'] = input("AppCenter API key: ")
