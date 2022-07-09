import json
import requests
from typing import Union
from datetime import datetime, timedelta
from appcenter_rtc.config.app_center import ac_config


class AppCenter:
    """
    Simple AppCenter API communication class
    Certain endpoints (I.E., POST/PATCH) need API keys with write permissions
    """

    def __init__(self, api_key: str):
        """
        :param api_key: User or App API token
        """
        self.__config = ac_config

        self.__config['api_key'] = api_key

    def get_app_list(self) -> Union[list, dict]:
        """
        Fetches the Apps available for the given USER API TOKEN
        :return: App list
        """
        url = self.__config['host'] + self.__config['api_version'] + self.__config['apps_endpoint']
        headers = {'X-API-Token': f'{self.__config["api_key"]}', 'Accept': 'application/json'}
        response = requests.get(f"{url}", headers=headers)

        return response.json()

    def get_app_versions(self, app: str, top: str = "10", start: str = None) -> dict:
        """
        Fetches the available versions for a given App in a defined period
        :return: App version list
        """

        # Start date defaults to a one-month period
        if not start:
            date = datetime.now() - timedelta(30)
            start = date.strftime('%Y-%m-%d')

        url = self.__config['host'] \
              + self.__config['api_version'] \
              + self.__config['versions_endpoint'] \
                  .replace("{{owner_name}}", self.__config['owner_name']) \
                  .replace("{{app_name}}", app) \
                  .replace("{{start_date}}", start) \
                  .replace("{{top}}", top)
        headers = {'X-API-Token': f'{self.__config["api_key"]}', 'Accept': 'application/json'}
        response = requests.get(f"{url}", headers=headers)

        return response.json()

    def get_error_group_list(self, app: str, version: str, top: int = 10, start: str = None,
                             order_by: str = "count desc", error_type: str = 'all') -> dict:
        """
        ErrorGroup GET returns an ordered list of every error group, limited by the top param
        It does NOT accept filters (a specific endpoint is used for Error Group searches)
        :param app: AppCenter Application name
        :param version: App version (x.xx.xx)
        :param top: Amount of top results
        :param start: Start date for error occurrence
        :param order_by: Order by column
        :param error_type: Type of error group
        :return: Error group list as json string
        """

        # Start date defaults to a one-month period
        if not start:
            date = datetime.now() - timedelta(30)
            start = date.strftime('%Y-%m-%d')

        url = self.__config['host'] \
              + self.__config['api_version'] \
              + self.__config['groups_endpoint'] \
                  .replace("{{owner_name}}", self.__config['owner_name']) \
                  .replace("{{app_name}}", app)
        headers = {'X-API-Token': f'{self.__config["api_key"]}', 'Accept': 'application/json'}
        response = requests.get(
            f"{url}"
            f"?version={version}"
            f"&start={start}"
            f"&$orderby={order_by}"
            f"&$top={top}"
            f"&errorType={error_type}",
            headers=headers
        )

        return response.json()

    def exception(self, app: str, error_group_id: str) -> dict:
        """
        ErrorGroup Exceptions GET returns a list of exception frames related to the error group
        :param app: AppCenter Application name
        :param error_group_id: Error group ID
        :return: Exception frame stacks as json string
        """
        url = self.__config['host'] \
              + self.__config['api_version'] \
              + self.__config['exceptions_endpoint'] \
                  .replace("{{owner_name}}", self.__config['owner_name']) \
                  .replace("{{app_name}}", app) \
                  .replace("{{error_group_id}}", error_group_id)
        headers = {'X-API-Token': f'{self.__config["api_key"]}', 'Accept': 'application/json'}

        response = requests.get(url, headers=headers)

        return response.json()

    def patch(self, app: str, error_group_id: str, annotation: str) -> int:
        """
        PATCH endpoint to create/update error group state and annotation.
        The state field is required and accepts values OPEN/CLOSED
        :param app: AppCenter Application name
        :param error_group_id: Error group ID
        :param annotation: Annotation string to be added/edited
        :return: Response status code
        """
        url = self.__config['host'] \
              + self.__config['api_version'] \
              + self.__config['exceptions_endpoint'] \
                  .replace("{{owner_name}}", self.__config['owner_name']) \
                  .replace("{{app_name}}", app) \
                  .replace("{{error_group_id}}", error_group_id)
        data = json.dumps({'state': 'open', 'annotation': annotation})
        headers = {'X-API-Token': f'{self.__config["api_key"]}', 'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        response = requests.patch(url, data=data, headers=headers)

        return response.status_code
