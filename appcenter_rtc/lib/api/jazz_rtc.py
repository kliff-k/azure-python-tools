import json
import requests
import xmltodict
from urllib.parse import quote
from appcenter_rtc.config.jazz_rtc import rtc_config


class JazzRtc:
    """
    Simple Jazz OSLC API communication class
    """

    def __init__(self, user: str, password: str):
        """
        Class initializer needs user credentials for Jazz login and session cookie creation used for following requests
        :param user: User ID
        :param password: User password
        """
        self.__config = rtc_config

        self.__config['user'] = user
        self.__config['pass'] = password
        self.__request = requests.Session()

        self.login_status = self.__login()

    def get(self, wi_id: str, wi_format: str = "json") -> str:
        """
        GET work item information
        :param wi_id: Work item ID
        :param wi_format: Response format (json,xml,html)
        :return: Work Item string
        """

        url = self.__config['host'] + self.__config['get_endpoint'] + f"{wi_id}.{wi_format}"

        return self.__request.get(url, verify=False).json()

    def post(self, data: str) -> dict:
        """
        POST endpoint to create a new work item with a JSON payload
        :param data: RTC OSLC payload
        :return: Json response with the created work item information
        """

        # Replaces any HOST slug in the payload
        data = json.loads(data.replace("{{host}}", self.__config['host']))

        url = self.__config['host'] + self.__config['post_endpoint'].replace("{{context_id}}", data['rtc_cm:contextId'])
        headers = {'Content-Type': 'application/x-oslc-cm-change-request+json; charset=utf-8', 'Accept': 'text/json'}

        return self.__request.post(url, data=json.dumps(data), headers=headers, verify=False).json()

    def query_work_items(self, query: str) -> list:
        """
        Queries work items using OSLC query syntax
        :query: OSLC query string
        :return: Work Item list
        """
        return []

    def project_areas(self) -> dict:
        """
        Fetches every project area in the Jazz RTC instance
        :return: Project area dictionary
        """
        url = self.__config['host'] + self.__config['project_areas_endpoint']
        response = self.__request.get(url, verify=False).text

        # Parse response XML into dictionary
        areas = xmltodict.parse(response)['foundation']['projectArea']

        # Iterate over the dictionary to return only the name and context ID
        area_dict = {}
        for area in areas:
            area_dict[area['name']] = area['contextId']

        return area_dict

    def members(self, context_id, search_term) -> dict:
        """
        Searches for a member in a given project
        :return: Project area dictionary
        """

        url = self.__config['host'] + self.__config['search_member_endpoint'] \
            .replace("{{context_id}}", context_id) \
            .replace("{{search_term}}", search_term)

        response = self.__request.get(url, verify=False).text

        # Parse response XML into dictionary
        soap = xmltodict.parse(response)
        members = soap['soapenv:Envelope']['soapenv:Body']['response']['returnValue']['value']['members']['elements']

        # Iterate over the dictionary to return only the name and context ID
        member_dict = {}
        for member in members:
            member_dict[member['name']] = member['userId']

        return member_dict

    def timeline_iterations(self, context_id) -> dict:
        """
        Fetches timelines and their iterations by context_id
        :return: Timeline and iteration dictionary
        """

        url = self.__config['host'] + self.__config['timeline_endpoint'].replace("{{context_id}}", context_id)

        response = self.__request.get(url, verify=False).text

        # Parse response XML into dictionary
        timelines = xmltodict.parse(response)['foundation']['developmentLine']

        return timelines

    def teams(self, context_id) -> dict:
        """
        Fetches teams by context_id
        :return: Timeline and iteration dictionary
        """

        url = self.__config['host'] + self.__config['teams_endpoint'].replace("{{context_id}}", context_id)

        response = self.__request.get(url, verify=False).text

        # Parse response XML into dictionary
        teams = xmltodict.parse(response)['foundation']['teamArea']

        return teams

    def url(self, wi_community, wi_id) -> str:
        """
        Assembles Work Item URL from host, community and id
        :param wi_community: Work Item Community name
        :param wi_id: Work Item ID
        :return: Work Item URL string
        """
        action = "#action=com.ibm.team.workitem.viewWorkItem&id="
        return f"{self.__config['host']}{self.__config['project_endpoint']}{quote(wi_community)}{action}{wi_id}"

    def __login(self) -> int:
        """
        Logs in user through credential filled form and stores cookie in requests session
        :return: Response status code
        """
        url = self.__config['host'] + self.__config['login_endpoint']
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'j_username': self.__config['user'],
            'j_password': self.__config['pass']
        }

        return self.__request.post(url, data=data, headers=headers, verify=False).status_code
