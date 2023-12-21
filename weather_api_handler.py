from typing import Final, Union, List
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

    def get_response(self, method: str, location: str, days: str) -> requests.Response:
        request_url: str = ''
        if method == 'current':
            request_url: str = f"{self.BASE_API_URL}/{method}.json?key={self.API_KEY}&q={location}"
        elif method == 'forecast':
            request_url: str = f"{self.BASE_API_URL}/{method}.json?key={self.API_KEY}&q={location}&days={days}"
        headers: dict = {'Content-Type': 'application/json'}
        weather_response: requests.Response = requests.post(url=request_url, headers=headers)
        log.logger.debug(f"The following request has been sent: {request_url}, headers: {headers}")
        log.logger.debug(f"The following response has been received: "
                         f"status: {weather_response.status_code}, text: {weather_response.text}")
        return weather_response


class ResponseFormatter:
    def __init__(self, response, com_type: str):
        self.response: requests.Response = response
        self.com_type: str = com_type
        self.answer = None
        if com_type == 'current':
            self.to_user: Union[dict, None] = self.format_response_current()
            if isinstance(self.to_user, dict):
                self.answer: str = self.form_usermsg_current()
        elif com_type == 'forecast':
            self.to_user: Union[dict, None] = self.format_response_forecast()
            if isinstance(self.to_user, dict):
                self.answer: str = self.form_usermsg_forecast()

    @staticmethod
    def find_location(location: dict) -> tuple:
        city: str = location.get('name')
        region: str = location.get('region')
        country: str = location.get('country')
        return city, region, country

    def format_response_current(self) -> Union[dict, None]:
        try:
            response = self.response.json()
        except json.JSONDecodeError as err:
            log.logger.error(err)
            return None
        else:
            current: dict = response.get('current')
            location: dict = response.get('location')
            temp_c: float = current.get('temp_c')
            cond: str = current.get('condition').get('text')
            wind_vel: float = current.get('wind_kph')
            city, region, country = self.find_location(location)
            return {'temp_c': temp_c, 'cond': cond, 'wind_vel': wind_vel,
                    'city': city, 'region': region, 'country': country}

    def format_response_forecast(self) -> Union[dict, None]:
        try:
            response = self.response.json()
        except json.JSONDecodeError as err:
            log.logger.error(err)
            return None
        else:
            location: dict = response.get('location')
            city, region, country = self.find_location(location)
            dt_lst: List[dict] = []
            for for_day in response.get('forecast').get('forecastday'):
                date: str = for_day.get('date')
                max_temp: float = for_day.get('day').get('maxtemp_c')
                min_temp: float = for_day.get('day').get('mintemp_c')
                avg_temp: float = for_day.get('day').get('avgtemp_c')
                max_wind: float = for_day.get('day').get('maxwind_kph')
                cond: str = for_day.get('day').get('condition').get('text')
                dt_lst.append({'date': date, 'max_temp': max_temp, 'min_temp': min_temp,
                               'avg_temp': avg_temp, 'max_wind': max_wind, 'cond': cond})
            return {'city': city, 'region': region, 'country': country, 'dt_lst': dt_lst}

    def form_usermsg_current(self) -> str:
        msg_for_user: str = f"Today in {self.to_user.get('city')}, {self.to_user.get('region')}, " \
                            f"{self.to_user.get('country')} you can see a {self.to_user.get('cond')}. " \
                            f"The temperature is {self.to_user.get('temp_c')} C degrees, " \
                            f"the velocity of the wind is {self.to_user.get('wind_vel')} km/h."
        return msg_for_user

    def form_usermsg_forecast(self) -> str:
        msg_for_user: str = f" {self.to_user.get('city')}, {self.to_user.get('region')}, " \
                            f"{self.to_user.get('country')}\n"
        for dt_info in self.to_user.get('dt_lst'):
            msg_for_user += f"date: {dt_info.get('date')},\tmax_temp: {dt_info.get('max_temp')},\t" \
                            f"min_temp: {dt_info.get('min_temp')},\tavg_temp: {dt_info.get('avg_temp')}\t" \
                            f"max_wind: {dt_info.get('max_wind')},\tcond: {dt_info.get('cond')}\n"
        return msg_for_user