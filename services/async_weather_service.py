"""
Async Weather Service.

This module provides the asynchronous implementation of the
weather service layer.

Responsibilities:
- Resolve city coordinates asynchronously.
- Fetch current weather from Open-Meteo.
- Fetch seven-day forecasts from Open-Meteo.
- Fetch weather for multiple cities concurrently.
- Map external API responses into domain models.
- Retry transient external API failures using bounded
  exponential backoff with jitter.
- Support externally managed HTTP sessions for application
  lifecycle integration.
- Record Prometheus metrics for external weather API calls.

Business logic, analytics, formatting, and presentation concerns
must not be implemented in this service.
"""

import asyncio
import random
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Awaitable, Callable

import aiohttp
import truststore

from weather_intelligence_agent_v2.config.city_resolver import (
    resolve_city,
)
from weather_intelligence_agent_v2.config.constants import (
    DAILY_FORECAST_FIELDS,
    GEOCODING_API,
    REQUEST_TIMEOUT,
    WEATHER_API,
    WEATHER_CODES,
)
from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
    ForecastDay,
)
from weather_intelligence_agent_v2.observability.weather_api_metrics import (
    WEATHER_API_DURATION_SECONDS,
    WEATHER_API_FAILURES_TOTAL,
    WEATHER_API_REQUESTS_TOTAL,
)


truststore.inject_into_ssl()


SleepCallable = Callable[
    [float],
    Awaitable[None],
]


@dataclass(
    slots=True,
    frozen=True,
)
class RetryConfig:
    """
    Configuration for transient HTTP retry behavior.

    Attributes:
        max_attempts:
            Maximum total number of request attempts,
            including the initial request.

        base_delay_seconds:
            Initial delay used by exponential backoff.

        max_delay_seconds:
            Maximum backoff delay before jitter.

        jitter_seconds:
            Maximum random jitter added to a retry delay.
    """

    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 5.0
    jitter_seconds: float = 0.25

    def __post_init__(
        self,
    ) -> None:
        """
        Validate retry configuration.
        """

        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be greater than or equal to 1."
            )

        if self.base_delay_seconds < 0:
            raise ValueError(
                "base_delay_seconds cannot be negative."
            )

        if self.max_delay_seconds < 0:
            raise ValueError(
                "max_delay_seconds cannot be negative."
            )

        if self.jitter_seconds < 0:
            raise ValueError(
                "jitter_seconds cannot be negative."
            )

        if (
            self.max_delay_seconds
            < self.base_delay_seconds
        ):
            raise ValueError(
                "max_delay_seconds must be greater than "
                "or equal to base_delay_seconds."
            )


class AsyncWeatherService:
    """
    Asynchronous weather service.

    This service is the asynchronous equivalent of the
    synchronous weather service.

    The service supports two resource ownership modes.

    Standalone mode:
        The service lazily creates its own ClientSession
        and is responsible for closing it.

    Application-managed mode:
        A ClientSession is injected by the application.
        The service uses but does not close that session.

    Public contract:
    - get_current_weather(city)
    - get_7_day_forecast(city)
    - get_weather_multiple(cities)
    """

    RETRYABLE_STATUS_CODES = frozenset(
        {
            429,
            500,
            502,
            503,
            504,
        }
    )

    def __init__(
        self,
        max_concurrency: int = 10,
        retry_config: RetryConfig | None = None,
        sleep_func: SleepCallable = asyncio.sleep,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        Initialize the asynchronous weather service.

        Args:
            max_concurrency:
                Maximum number of concurrent city-level
                weather operations.

            retry_config:
                Optional retry configuration.

            sleep_func:
                Async sleep callable used by retry logic.

            session:
                Optional externally managed aiohttp ClientSession.

                When supplied, the service does not own the session
                and therefore does not close it.

                When omitted, the service creates its own session
                lazily and is responsible for closing it.

        Raises:
            ValueError:
                If max_concurrency is less than one.
        """

        if max_concurrency < 1:
            raise ValueError(
                "max_concurrency must be greater than or equal to 1."
            )

        self._session = session

        self._owns_session = (
            session is None
        )

        self._semaphore = asyncio.Semaphore(
            max_concurrency
        )

        self._retry_config = (
            retry_config
            or RetryConfig()
        )

        self._sleep = sleep_func

    async def __aenter__(
        self,
    ) -> "AsyncWeatherService":
        """
        Enter the asynchronous context manager.

        Returns:
            Initialized service instance.
        """

        await self._ensure_session()

        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        """
        Exit the asynchronous context manager.

        Only sessions owned by this service are closed.
        """

        await self.close()

    async def _ensure_session(
        self,
    ) -> aiohttp.ClientSession:
        """
        Ensure an active HTTP session exists.

        Returns:
            Active aiohttp ClientSession.

        Raises:
            RuntimeError:
                If an externally managed session was closed
                unexpectedly.
        """

        if self._session is not None:

            if self._session.closed:

                if not self._owns_session:
                    raise RuntimeError(
                        "The externally managed aiohttp "
                        "ClientSession is closed."
                    )

                self._session = None

            else:
                return self._session

        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT
        )

        self._session = aiohttp.ClientSession(
            timeout=timeout
        )

        self._owns_session = True

        return self._session

    async def close(
        self,
    ) -> None:
        """
        Close resources owned by this service.

        An externally injected ClientSession is not closed because
        its lifecycle belongs to the application that created it.
        """

        if not self._owns_session:
            return

        if (
            self._session is not None
            and not self._session.closed
        ):
            await self._session.close()

        self._session = None

    def _calculate_backoff_delay(
        self,
        attempt: int,
    ) -> float:
        """
        Calculate exponential backoff delay with jitter.

        Args:
            attempt:
                Current attempt number starting from one.

        Returns:
            Delay in seconds.
        """

        exponential_delay = (
            self._retry_config.base_delay_seconds
            * (2 ** (attempt - 1))
        )

        bounded_delay = min(
            exponential_delay,
            self._retry_config.max_delay_seconds,
        )

        jitter = random.uniform(
            0.0,
            self._retry_config.jitter_seconds,
        )

        return (
            bounded_delay
            + jitter
        )

    def _get_retry_after_seconds(
        self,
        response: aiohttp.ClientResponse,
    ) -> float | None:
        """
        Read Retry-After header expressed in seconds.

        Args:
            response:
                HTTP response.

        Returns:
            Retry delay in seconds, or None when unavailable.
        """

        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after is None:
            return None

        try:
            delay = float(
                retry_after
            )
        except ValueError:
            return None

        return max(
            0.0,
            delay,
        )

    @staticmethod
    def _get_metric_endpoint(
        url: str,
    ) -> str:
        """
        Return a stable logical endpoint name for weather API metrics.

        Args:
            url:
                External weather API URL.

        Returns:
            Low-cardinality logical endpoint name.
        """

        if "geocoding-api.open-meteo.com" in url:
            return "geocoding"

        if "api.open-meteo.com" in url:
            return "forecast"

        return "unknown"

    async def _get_json(
        self,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a resilient asynchronous HTTP GET request.

        Retryable conditions:
        - HTTP 429
        - HTTP 500
        - HTTP 502
        - HTTP 503
        - HTTP 504
        - aiohttp client/network errors
        - asyncio timeout errors

        Non-retryable HTTP errors fail immediately.

        Prometheus metrics record one logical external API operation,
        including all retry attempts and backoff time.

        Args:
            url:
                Target API URL.

            params:
                Query parameters.

        Returns:
            Parsed JSON response.
        """

        endpoint = self._get_metric_endpoint(
            url
        )

        WEATHER_API_REQUESTS_TOTAL.labels(
            endpoint=endpoint,
        ).inc()

        start_time = perf_counter()

        try:
            session = await self._ensure_session()

            for attempt in range(
                1,
                self._retry_config.max_attempts + 1,
            ):
                try:

                    async with session.get(
                        url,
                        params=params,
                    ) as response:

                        if (
                            response.status
                            in self.RETRYABLE_STATUS_CODES
                        ):

                            if (
                                attempt
                                >= self._retry_config.max_attempts
                            ):
                                response.raise_for_status()

                            retry_after = (
                                self._get_retry_after_seconds(
                                    response
                                )
                            )

                            delay = (
                                retry_after
                                if retry_after is not None
                                else self._calculate_backoff_delay(
                                    attempt
                                )
                            )

                            await self._sleep(
                                delay
                            )

                            continue

                        response.raise_for_status()

                        data: dict[str, Any] = (
                            await response.json()
                        )

                        return data

                except aiohttp.ClientResponseError:
                    raise

                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                ):

                    if (
                        attempt
                        >= self._retry_config.max_attempts
                    ):
                        raise

                    delay = (
                        self._calculate_backoff_delay(
                            attempt
                        )
                    )

                    await self._sleep(
                        delay
                    )

            raise RuntimeError(
                "HTTP retry loop exited unexpectedly."
            )

        except Exception:
            WEATHER_API_FAILURES_TOTAL.labels(
                endpoint=endpoint,
            ).inc()

            raise

        finally:
            WEATHER_API_DURATION_SECONDS.labels(
                endpoint=endpoint,
            ).observe(
                perf_counter()
                - start_time
            )

    async def _get_coordinates(
        self,
        city: str,
    ) -> tuple[
        float,
        float,
        str,
    ]:
        """
        Resolve a city into geographic coordinates.

        Args:
            city:
                City name.

        Returns:
            Latitude, longitude, and country.

        Raises:
            ValueError:
                If the city cannot be found.
        """

        resolved_city = resolve_city(
            city
        )

        data = await self._get_json(
            GEOCODING_API,
            params={
                "name": resolved_city,
                "count": 1,
            },
        )

        results = data.get(
            "results"
        )

        if not results:
            raise ValueError(
                f"City '{resolved_city}' not found."
            )

        location = results[0]

        return (
            float(
                location["latitude"]
            ),
            float(
                location["longitude"]
            ),
            location.get(
                "country",
                "Unknown",
            ),
        )

    async def get_current_weather(
        self,
        city: str,
    ) -> CurrentWeather:
        """
        Retrieve current weather for a city.

        Args:
            city:
                City name.

        Returns:
            CurrentWeather domain model.
        """

        (
            latitude,
            longitude,
            country,
        ) = await self._get_coordinates(
            city
        )

        data = await self._get_json(
            WEATHER_API,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
            },
        )

        weather = data[
            "current_weather"
        ]

        return CurrentWeather(
            city=city,
            country=country,
            temperature=float(
                weather[
                    "temperature"
                ]
            ),
            wind_speed=float(
                weather[
                    "windspeed"
                ]
            ),
            wind_direction=float(
                weather[
                    "winddirection"
                ]
            ),
            condition=WEATHER_CODES.get(
                weather[
                    "weathercode"
                ],
                "Unknown",
            ),
            observation_time=weather[
                "time"
            ].replace(
                "T",
                " ",
            ),
        )

    async def get_7_day_forecast(
        self,
        city: str,
    ) -> Forecast:
        """
        Retrieve the seven-day weather forecast.

        Args:
            city:
                City name.

        Returns:
            Forecast domain model.
        """

        (
            latitude,
            longitude,
            country,
        ) = await self._get_coordinates(
            city
        )

        data = await self._get_json(
            WEATHER_API,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": ",".join(
                    DAILY_FORECAST_FIELDS
                ),
                "forecast_days": 7,
                "timezone": "auto",
            },
        )

        daily = data[
            "daily"
        ]

        forecast_days: list[
            ForecastDay
        ] = []

        for index in range(
            len(
                daily["time"]
            )
        ):

            forecast_day = ForecastDay(
                date=daily[
                    "time"
                ][index],
                condition=WEATHER_CODES.get(
                    daily[
                        "weathercode"
                    ][index],
                    "Unknown",
                ),
                max_temperature=float(
                    daily[
                        "temperature_2m_max"
                    ][index]
                ),
                min_temperature=float(
                    daily[
                        "temperature_2m_min"
                    ][index]
                ),
                rain_probability=int(
                    daily[
                        "precipitation_probability_max"
                    ][index]
                ),
            )

            forecast_days.append(
                forecast_day
            )

        return Forecast(
            city=city,
            country=country,
            forecast_days=forecast_days,
        )

    async def _get_current_weather_limited(
        self,
        city: str,
    ) -> CurrentWeather:
        """
        Retrieve weather while respecting concurrency limits.

        Args:
            city:
                City name.

        Returns:
            CurrentWeather domain model.
        """

        async with self._semaphore:

            return await self.get_current_weather(
                city
            )

    async def get_weather_multiple(
        self,
        cities: list[str],
    ) -> list[CurrentWeather]:
        """
        Retrieve current weather for multiple cities concurrently.

        Args:
            cities:
                City names.

        Returns:
            CurrentWeather objects in input order.
        """

        if not cities:
            return []

        tasks = [
            self._get_current_weather_limited(
                city
            )
            for city in cities
        ]

        results = await asyncio.gather(
            *tasks
        )

        return list(
            results
        )