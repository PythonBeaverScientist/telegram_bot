from typing import Final
import json
import requests
from base_log import LoggerHand

log = LoggerHand(__name__, f"loggers/{__name__}.log")


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
        log.logger.debug(f"The following request has been sent: {request_url}, headers: {headers}")
        log.logger.debug(f"The following response has been received: "
                         f"status: {weather_response.status_code}, text: {weather_response.text}")
        return weather_response
