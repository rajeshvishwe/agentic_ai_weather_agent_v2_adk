import asyncio

from weather_intelligence_agent_v2.services.async_weather_service import AsyncWeatherService


async def main():

    cities = [

        "Delhi",

        "Mumbai",

        "London",

        "Tokyo",

        "Dubai"
    ]

    async with AsyncWeatherService() as service:

        weather = await service.get_weather_multiple(cities)

        for city in weather:

            print(city)


if __name__ == "__main__":

    asyncio.run(main())