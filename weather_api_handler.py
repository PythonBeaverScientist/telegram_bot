from typing import Final, Union, List
import json
import aiohttp
import asyncio
from base_log import LoggerHand
from weather_model import WeatherModel
from datetime import datetime
from db_orm import add_new_weather

log = LoggerHand(__name__, f"loggers/{__name__}.log")


class BaseRequest:

    def __init__(self):
        with open('credentials/weather_api_verification.json', 'r') as file:
            api_ver: dict = json.load(file)

        self.API_KEY: Final[str] = api_ver['api_key']
        self.BASE_API_URL: Final[str] = api_ver['base_api_url']
        self.headers: dict = {'Content-Type': 'application/json'}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def get_response(self, method: str, location: str, days: str) -> aiohttp.ClientResponse:
        request_url: str = ''
        if method == 'current':
            request_url: str = f"{self.BASE_API_URL}/{method}.json?key={self.API_KEY}&q={location}"
        elif method == 'forecast':
            request_url: str = f"{self.BASE_API_URL}/{method}.json?key={self.API_KEY}&q={location}&days={days}"
        weather_response: aiohttp.ClientResponse = await self.session.post(request_url, headers=self.headers)
        log.logger.debug(f"The following request has been sent: {request_url}, headers: {self.headers}")
        log.logger.debug(f"The following response has been received: "
                         f"status: {weather_response.status}, text: {weather_response.text}")
        return weather_response

    async def close_session(self):
        await self.session.close()


class ResponseFormatter:
    def __init__(self, response: aiohttp.ClientResponse, com_type: str):
        self.response: aiohttp.ClientResponse = response
        self.com_type: str = com_type
        self.answer = None

    @staticmethod
    def find_location(location: dict) -> tuple:
        city: str = location.get('name')
        region: str = location.get('region')
        country: str = location.get('country')
        return city, region, country

    async def format_response_current(self) -> Union[WeatherModel, None]:
        try:
            response = await self.response.json()
        except json.JSONDecodeError as err:
            log.logger.error(err)
            return None
        else:
            weather: WeatherModel = WeatherModel()
            current: dict = response.get('current')
            location: dict = response.get('location')
            weather.w_date = datetime.now().date()
            weather.avg_temp = current.get('temp_c')
            weather.condition = current.get('condition').get('text')
            weather.wind_vel = current.get('wind_kph')
            weather.city, weather.region, weather.country = self.find_location(location)
            return weather

    async def format_response_forecast(self) -> Union[List[WeatherModel], None]:
        try:
            response = await self.response.json()
        except json.JSONDecodeError as err:
            log.logger.error(err)
            return None
        else:
            w_lst: list = []
            location: dict = response.get('location')
            for for_day in response.get('forecast').get('forecastday'):
                weather = WeatherModel()
                weather.city, weather.region, weather.country = self.find_location(location)
                weather.w_date = datetime.strptime(for_day.get('date'), '%Y-%m-%d')
                weather.max_temp = for_day.get('day').get('maxtemp_c')
                weather.min_temp = for_day.get('day').get('mintemp_c')
                weather.avg_temp = for_day.get('day').get('avgtemp_c')
                weather.wind_vel = for_day.get('day').get('maxwind_kph')
                weather.condition = for_day.get('day').get('condition').get('text')
                w_lst.append(weather)
            return w_lst

    @staticmethod
    def form_usermsg_current(db_user_request, engine, to_user: WeatherModel) -> str:
        msg_for_user: str = f"Today in {to_user.city}, {to_user.region}, " \
                            f"{to_user.country} you can see a {to_user.condition}. " \
                            f"The temperature is {to_user.avg_temp} C degrees, " \
                            f"the velocity of the wind is {to_user.wind_vel} km/h."
        add_new_weather(db_user_request, engine, to_user)
        return msg_for_user

    @staticmethod
    def form_usermsg_forecast(db_user_request, engine, w_lst: List[WeatherModel]) -> str:
        msg_for_user: str = f" {w_lst[0].city}, {w_lst[0].region}, " \
                            f"{w_lst[0].country}\n"
        for weather in w_lst:
            msg_for_user += f"date: {weather.w_date},\tmax_temp: {weather.max_temp},\t" \
                            f"min_temp: {weather.min_temp},\tavg_temp: {weather.avg_temp}\t" \
                            f"max_wind: {weather.wind_vel},\tcondition: {weather.condition}\n"
            add_new_weather(db_user_request, engine, weather)
        return msg_for_user

    async def get_ready_answer(self, db_user_request, engine) -> str:
        if self.com_type == 'current':
            to_user: Union[WeatherModel, None] = await asyncio.create_task(self.format_response_current())
            if isinstance(to_user, WeatherModel):
                answer: str = self.form_usermsg_current(db_user_request, engine, to_user)
                return answer
        elif self.com_type == 'forecast':
            to_user: Union[List[WeatherModel], None] = await asyncio.create_task(self.format_response_forecast())
            if isinstance(to_user, list):
                answer: str = self.form_usermsg_forecast(db_user_request, engine, to_user)
                return answer
