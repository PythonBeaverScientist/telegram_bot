from typing import Final
import json
import requests


class BaseRequest:

    def __init__(self):
        with open('credentials/weather_api_verification.json', 'r') as file:
            api_ver: dict = json.load(file)

        self.API_KEY: Final[str] = api_ver['api_key']
        self.BASE_API_URL: Final[str] = api_ver['base_api_url']

    def get_response(self, method: str, location: str) -> requests.Response:
        request_url: str = f"{self.BASE_API_URL}/{method}.json?key={self.API_KEY}&q={location}"
        headers: dict = {'Content-Type': 'application/json'}
        weather_response: requests.Response = requests.post(url=request_url, headers=headers)
        return weather_response
