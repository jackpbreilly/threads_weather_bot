from threadspy.client import *

import asyncio
import aiohttp

import json
import time

from dotenv import load_dotenv
load_dotenv()

class Weather:
    """Class to manage getting weather data from WeatherAPI.com"""
    def __init__(self, key) -> None:
        self.key = key

    async def __aenter__(self) -> None:
        self.session = await self.new_session()
        return self

    async def __aexit__(self, *args) -> None:
        await self.session.close()

    async def new_session(self) -> aiohttp.ClientSession:
         return aiohttp.ClientSession(trust_env=True)    

    async def get_current_weather(self, loc) -> str:
        async with self.session.get(f"https://api.weatherapi.com/v1/current.json?q={loc}&key={self.key}") as res:
            data = await res.text()
            return data

class Bot:
    """ Class to manage bot"""
    def __init__(self, threads_api) -> None:
        self.theads_api = threads_api

    async def __aenter__(self) -> None:
        return self

    async def __aexit__(self, *args) -> None:
        pass 
    
    async def setup(self):
        await self.theads_api.login(os.environ["THREADS_USERNAME"],os.environ["THREADS_PASSWORD"])
    
    async def post(self, message):
        await self.theads_api.post_message(message)
    
async def main():
    """Driver function"""
    async with Client() as threads_api:
        async with Bot(threads_api) as bot:
            await bot.setup()
            async with Weather(key=os.environ["API_KEY"]) as weather:
                while True:
                    raw_data = await weather.get_current_weather(loc=os.environ["LOCATION"])
                    data = dict(json.loads(raw_data))
                    await bot.post(f"{data['location']['name']} is a {data['current']['condition']['text']} {data['current']['temp_c']}")
                    time.sleep(300)

asyncio.run(main())